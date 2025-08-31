# Prevent __pycache__ creation
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import subprocess
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from packaging import version

@dataclass
class Program:
    name: str
    version: str
    publisher: str = ""
    install_location: str = ""
    update_available: bool = False
    available_version: str = ""
    source: str = ""
    package_id: str = ""

class ProgramDetector:
    def __init__(self):
        self.programs = []
    
    def scan_installed_programs(self) -> List[Program]:
        """Scan for all installed programs"""
        self.programs = []
        
        # Try multiple detection methods
        self._scan_winget()
        self._scan_registry()
        self._scan_chocolatey()
        
        # Remove duplicates
        self._deduplicate_programs()
        
        return self.programs
    
    def _scan_winget(self):
        """Scan using Windows Package Manager"""
        try:
            result = subprocess.run(
                ["winget", "list", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',  # Ignore encoding errors
                timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                self._parse_winget_output(result.stdout)
            else:
                pass
                
        except FileNotFoundError:
            pass
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            pass
    
    def _parse_winget_output(self, output: str):
        """Parse winget list output"""
        lines = output.split('\n')
        header_found = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip until we find the header
            if "Name" in line and "Id" in line and "Version" in line:
                header_found = True
                continue
            
            if not header_found or line.startswith('-'):
                continue
            
            # Parse the line - winget output is space-separated with variable spacing
            parts = re.split(r'\s{2,}', line)
            if len(parts) >= 3:
                name = parts[0].strip()
                package_id = parts[1].strip() if len(parts) > 1 else ""
                version_str = parts[2].strip() if len(parts) > 2 else "Unknown"
                
                # Ensure we have a valid name
                if not name or name == "Unknown":
                    continue
                
                # Skip if already exists
                if not any(p.name == name for p in self.programs):
                    program = Program(
                        name=name,
                        version=version_str,
                        package_id=package_id,
                        source="winget"
                    )
                    self.programs.append(program)
    
    def _scan_registry(self):
        """Scan Windows registry for installed programs"""
        try:
            # Query both 32-bit and 64-bit registry locations
            registry_paths = [
                r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for reg_path in registry_paths:
                try:
                    result = subprocess.run(
                        ["reg", "query", reg_path, "/s"],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore',  # Ignore encoding errors
                        timeout=60,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        self._parse_registry_output(result.stdout)
                        
                except subprocess.TimeoutExpired:
                    pass
                except Exception as e:
                    pass
            
        except Exception as e:
            pass
    
    def _parse_registry_output(self, output: str):
        """Parse registry query output"""
        if not output:
            return
            
        current_key = None
        current_program = {}
        
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # New registry key
            if line.startswith('HKEY_'):
                # Save previous program if valid
                if current_program and self._is_valid_program(current_program):
                    self._add_registry_program(current_program)
                
                current_key = line
                current_program = {}
                continue
            
            # Registry value
            if '\t' in line or '    ' in line:
                parts = re.split(r'\s+', line, 2)
                if len(parts) >= 3:
                    value_name = parts[0]
                    value_type = parts[1]
                    value_data = parts[2] if len(parts) > 2 else ""
                    
                    if value_name == "DisplayName":
                        current_program['name'] = value_data
                    elif value_name == "DisplayVersion":
                        current_program['version'] = value_data
                    elif value_name == "Publisher":
                        current_program['publisher'] = value_data
                    elif value_name == "InstallLocation":
                        current_program['install_location'] = value_data
        
        # Don't forget the last program
        if current_program and self._is_valid_program(current_program):
            self._add_registry_program(current_program)
    
    def _is_valid_program(self, program_data: Dict) -> bool:
        """Check if registry entry represents a valid program"""
        if not program_data.get('name'):
            return False
        
        name = program_data['name'].lower()
        
        # Skip system components, updates, and redistributables
        skip_keywords = [
            'hotfix', 'security update', 'kb', 'update for',
            'redistributable', 'runtime', 'microsoft visual c++',
            'service pack', 'language pack', '.net framework'
        ]
        
        for keyword in skip_keywords:
            if keyword in name:
                return False
        
        return True
    
    def _add_registry_program(self, program_data: Dict):
        """Add program from registry data"""
        name = program_data.get('name', '')
        
        # Skip if already exists
        if any(p.name == name for p in self.programs):
            return
        
        program = Program(
            name=name,
            version=program_data.get('version', 'Unknown'),
            publisher=program_data.get('publisher', ''),
            install_location=program_data.get('install_location', ''),
            source="registry"
        )
        self.programs.append(program)
    
    def _scan_chocolatey(self):
        """Scan using Chocolatey if available"""
        try:
            result = subprocess.run(
                ["choco", "list", "--local-only"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',  # Ignore encoding errors
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                self._parse_chocolatey_output(result.stdout)
            else:
                pass
                
        except FileNotFoundError:
            pass
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            pass
    
    def _parse_chocolatey_output(self, output: str):
        """Parse chocolatey list output"""
        for line in output.split('\n'):
            line = line.strip()
            if not line or line.startswith('Chocolatey'):
                continue
            
            # Format: "package-name version"
            parts = line.split(' ')
            if len(parts) >= 2:
                name = parts[0]
                version_str = parts[1]
                
                # Skip if already exists
                if not any(p.package_id == name for p in self.programs):
                    program = Program(
                        name=name.replace('-', ' ').title(),
                        version=version_str,
                        package_id=name,
                        source="chocolatey"
                    )
                    self.programs.append(program)
    
    def _deduplicate_programs(self):
        """Remove duplicate programs, preferring winget over others"""
        seen = {}
        unique_programs = []
        
        # Sort by priority: winget > chocolatey > registry
        priority = {"winget": 1, "chocolatey": 2, "registry": 3}
        self.programs.sort(key=lambda p: priority.get(p.source, 4))
        
        for program in self.programs:
            # Use normalized name as key
            key = program.name.lower().strip()
            
            if key not in seen:
                seen[key] = program
                unique_programs.append(program)
            else:
                # Keep the one with higher priority (lower number)
                existing = seen[key]
                if priority.get(program.source, 4) < priority.get(existing.source, 4):
                    # Replace with higher priority program
                    seen[key] = program
                    unique_programs = [p for p in unique_programs if p != existing]
                    unique_programs.append(program)
        
        self.programs = unique_programs
