import subprocess
import re
from typing import List, Dict, Optional
from packaging import version
from program_detector import Program
from config_manager import get_config

class UpdateChecker:
    def __init__(self):
        self.config = get_config()
    
    def check_for_updates(self, programs: List[Program]) -> List[Program]:
        """Check for updates for all programs"""
        
        updated_programs = []
        
        for program in programs:
            # Skip excluded programs
            if self.config.is_program_excluded(program.name, program.publisher):
                continue
            
            # Check for updates based on source
            if program.source == "winget" and self.config.get('update_sources.winget.enabled'):
                self._check_winget_updates(program)
            elif program.source == "chocolatey" and self.config.get('update_sources.chocolatey.enabled'):
                self._check_chocolatey_updates(program)
            elif self.config.get('update_sources.custom.enabled'):
                self._check_custom_updates(program)
            
            updated_programs.append(program)
        
        updates_available = sum(1 for p in updated_programs if p.update_available)
        
        return updated_programs
    
    def _check_winget_updates(self, program: Program):
        """Check for updates using winget"""
        try:
            if not program.package_id:
                return
            
            # Use winget upgrade to check for updates
            result = subprocess.run(
                ["winget", "upgrade", "--id", program.package_id, "--exact", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )
            
            # Winget upgrade with no --accept will show what would be updated
            if "upgrade available" in result.stdout.lower() or "available" in result.stdout.lower():
                # Try to extract version from output
                version_match = re.search(r'(\d+\.\d+\.\d+[\.\d]*)', result.stdout)
                if version_match:
                    program.available_version = version_match.group(1)
                    program.update_available = True
                else:
                    program.update_available = True
                    program.available_version = "Unknown"
            
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            pass
    
    def _check_chocolatey_updates(self, program: Program):
        """Check for updates using chocolatey"""
        try:
            if not program.package_id:
                return
            
            result = subprocess.run(
                ["choco", "upgrade", program.package_id, "--noop"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )
            
            if "would like to upgrade" in result.stdout.lower():
                # Extract version from chocolatey output
                version_match = re.search(rf'{program.package_id} v(\d+\.\d+\.\d+[\.\d]*)', result.stdout)
                if version_match:
                    program.available_version = version_match.group(1)
                    program.update_available = True
                else:
                    program.update_available = True
                    program.available_version = "Unknown"
            
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            pass
    
    def _check_custom_updates(self, program: Program):
        """Check for updates using custom handlers for specific programs"""
        # Custom update checkers for popular software
        custom_checkers = {
            'chrome': self._check_chrome_update,
            'firefox': self._check_firefox_update,
            'vlc': self._check_vlc_update,
            'notepad++': self._check_notepadpp_update,
        }
        
        program_name_lower = program.name.lower()
        
        for name, checker in custom_checkers.items():
            if name in program_name_lower:
                try:
                    checker(program)
                    break
                except Exception as e:
                    pass
    
    def _check_chrome_update(self, program: Program):
        """Check Chrome version via winget as fallback"""
        try:
            result = subprocess.run(
                ["winget", "search", "Google.Chrome", "--exact"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=15
            )
            
            if result.returncode == 0:
                # Parse version from search result
                version_match = re.search(r'Google\.Chrome\s+(\d+\.\d+\.\d+[\.\d]*)', result.stdout)
                if version_match:
                    available_version = version_match.group(1)
                    try:
                        current_ver = version.parse(program.version.split()[0])
                        available_ver = version.parse(available_version)
                        if available_ver > current_ver:
                            program.available_version = available_version
                            program.update_available = True
                    except:
                        pass
        except Exception:
            pass
    
    def _check_firefox_update(self, program: Program):
        """Check Firefox version via winget as fallback"""
        try:
            result = subprocess.run(
                ["winget", "search", "Mozilla.Firefox", "--exact"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=15
            )
            
            if result.returncode == 0:
                version_match = re.search(r'Mozilla\.Firefox\s+(\d+\.\d+[\.\d]*)', result.stdout)
                if version_match:
                    available_version = version_match.group(1)
                    try:
                        current_ver = version.parse(program.version.split()[0])
                        available_ver = version.parse(available_version)
                        if available_ver > current_ver:
                            program.available_version = available_version
                            program.update_available = True
                    except:
                        pass
        except Exception:
            pass
    
    def _check_vlc_update(self, program: Program):
        """Check VLC version via winget as fallback"""
        try:
            result = subprocess.run(
                ["winget", "search", "VideoLAN.VLC", "--exact"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=15
            )
            
            if result.returncode == 0:
                version_match = re.search(r'VideoLAN\.VLC\s+(\d+\.\d+\.\d+)', result.stdout)
                if version_match:
                    available_version = version_match.group(1)
                    try:
                        current_ver = version.parse(program.version.split()[0])
                        available_ver = version.parse(available_version)
                        if available_ver > current_ver:
                            program.available_version = available_version
                            program.update_available = True
                    except:
                        pass
        except Exception:
            pass
    
    def _check_notepadpp_update(self, program: Program):
        """Check Notepad++ version via winget as fallback"""
        try:
            result = subprocess.run(
                ["winget", "search", "Notepad++.Notepad++", "--exact"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=15
            )
            
            if result.returncode == 0:
                version_match = re.search(r'Notepad\+\+\.Notepad\+\+\s+(\d+\.\d+[\.\d]*)', result.stdout)
                if version_match:
                    available_version = version_match.group(1)
                    try:
                        current_ver = version.parse(program.version.split()[0])
                        available_ver = version.parse(available_version)
                        if available_ver > current_ver:
                            program.available_version = available_version
                            program.update_available = True
                    except:
                        pass
        except Exception:
            pass
