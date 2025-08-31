# Prevent __pycache__ creation
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import subprocess
import threading
import time
from typing import List, Dict, Optional, Callable
from datetime import datetime
from pathlib import Path
from program_detector import Program
from config_manager import get_config

class UpdateResult:
    def __init__(self, program: Program):
        self.program = program
        self.success = False
        self.error_message = ""
        self.start_time = None
        self.end_time = None
        self.output = ""
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0

class UpdateInstaller:
    def __init__(self):
        self.config = get_config()
        self.active_updates = {}
        self.update_queue = []
        self.max_concurrent = self.config.get('update_behavior.max_concurrent_updates', 3)
    
    def install_updates(self, programs: List[Program], progress_callback: Optional[Callable] = None) -> Dict[str, UpdateResult]:
        """Install updates for the given programs"""
        
        # Filter programs that actually have updates
        programs_to_update = [p for p in programs if p.update_available]
        
        if not programs_to_update:
            return {}
        
        # Create backup if enabled
        if self.config.get('general.create_backups'):
            self._create_backup(programs_to_update)
        
        results = {}
        
        if self.config.get('update_behavior.update_all_at_once'):
            # Update all at once (sequential)
            for program in programs_to_update:
                result = self._install_single_update(program)
                results[program.name] = result
                if progress_callback:
                    progress_callback(program.name, result.success, len(results), len(programs_to_update))
        else:
            # Concurrent updates with limit
            results = self._install_concurrent_updates(programs_to_update, progress_callback)
        
        self._log_update_summary(results)
        return results
    
    def _install_single_update(self, program: Program) -> UpdateResult:
        """Install update for a single program"""
        result = UpdateResult(program)
        result.start_time = datetime.now()
        
        try:
            if program.source == "winget":
                success, output, error = self._install_winget_update(program)
            elif program.source == "chocolatey":
                success, output, error = self._install_chocolatey_update(program)
            else:
                success, output, error = self._install_custom_update(program)
            
            result.success = success
            result.output = output
            result.error_message = error
                
        except Exception as e:
            result.success = False
            result.error_message = str(e)
        
        result.end_time = datetime.now()
        return result
    
    def _install_concurrent_updates(self, programs: List[Program], progress_callback: Optional[Callable] = None) -> Dict[str, UpdateResult]:
        """Install updates concurrently with thread pool"""
        results = {}
        completed = 0
        total = len(programs)
        
        def update_worker(program):
            nonlocal completed
            result = self._install_single_update(program)
            results[program.name] = result
            completed += 1
            
            if progress_callback:
                progress_callback(program.name, result.success, completed, total)
        
        # Create and start threads
        threads = []
        active_threads = 0
        program_index = 0
        
        while program_index < len(programs) or active_threads > 0:
            # Start new threads up to the limit
            while active_threads < self.max_concurrent and program_index < len(programs):
                program = programs[program_index]
                thread = threading.Thread(target=update_worker, args=(program,))
                thread.start()
                threads.append(thread)
                active_threads += 1
                program_index += 1
            
            # Check for completed threads
            for thread in threads[:]:
                if not thread.is_alive():
                    thread.join()
                    threads.remove(thread)
                    active_threads -= 1
            
            time.sleep(0.1)  # Small delay to prevent busy waiting
        
        # Wait for all remaining threads
        for thread in threads:
            thread.join()
        
        return results
    
    def _install_winget_update(self, program: Program) -> tuple[bool, str, str]:
        """Install update using winget"""
        try:
            if not program.package_id:
                return False, "", "No package ID available"
            
            cmd = ["winget", "upgrade", "--id", program.package_id, "--exact", "--silent", "--accept-source-agreements", "--accept-package-agreements"]
            
            # Add download only flag if configured
            if self.config.get('update_behavior.download_only'):
                cmd.append("--download")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=600,  # 10 minute timeout
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Update timed out"
        except Exception as e:
            return False, "", f"Exception: {str(e)}"
    
    def _install_chocolatey_update(self, program: Program) -> tuple[bool, str, str]:
        """Install update using chocolatey"""
        try:
            if not program.package_id:
                return False, "", "No package ID available"
            
            cmd = ["choco", "upgrade", program.package_id, "-y"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=600,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Update timed out"
        except Exception as e:
            return False, "", f"Exception: {str(e)}"
    
    def _install_custom_update(self, program: Program) -> tuple[bool, str, str]:
        """Install update using custom method"""
        # For programs not available via winget or chocolatey,
        # we would need specific update mechanisms
        # This is a placeholder for custom update handlers
        
        return False, "", "Custom update not implemented"
    
    def _create_backup(self, programs: List[Program]):
        """Create backup before updates"""
        try:
            backup_dir = Path(self.config.get('general.backup_directory', 'backups'))
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"pre_update_backup_{timestamp}.txt"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(f"Backup created: {datetime.now()}\n")
                f.write("Programs to be updated:\n\n")
                
                for program in programs:
                    f.write(f"Name: {program.name}\n")
                    f.write(f"Current Version: {program.version}\n")
                    f.write(f"Available Version: {program.available_version}\n")
                    f.write(f"Source: {program.source}\n")
                    f.write(f"Package ID: {program.package_id}\n")
                    f.write("-" * 50 + "\n")
            
        except Exception as e:
            pass
    
    def _log_update_summary(self, results: Dict[str, UpdateResult]):
        """Log summary of update results"""
        successful = sum(1 for r in results.values() if r.success)
        failed = len(results) - successful
        total_time = sum(r.duration for r in results.values())
        pass
    
    def install_single_program(self, program: Program) -> UpdateResult:
        """Install update for a single program"""
        return self._install_single_update(program)
