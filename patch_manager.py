#!/usr/bin/env python3
"""
Windows Patch Manager
A comprehensive tool for managing software updates on Windows systems.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List
import json
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import get_config
from program_detector import ProgramDetector, Program
from update_checker import UpdateChecker
from update_installer import UpdateInstaller, UpdateResult
from colorama import init, Fore, Back, Style

try:
    from tabulate import tabulate
except ImportError:
    # Fallback if tabulate is not available
    def tabulate(data, headers=None, tablefmt="grid"):
        if not data:
            return ""
        
        # Simple table formatting fallback
        if headers:
            result = " | ".join(headers) + "\n"
            result += "-" * len(result) + "\n"
        else:
            result = ""
        
        for row in data:
            result += " | ".join(str(cell) for cell in row) + "\n"
        
        return result

# Initialize colorama for Windows terminal colors
init()

class PatchManager:
    def __init__(self):
        self.config = get_config()
        self.detector = ProgramDetector()
        self.checker = UpdateChecker()
        self.installer = UpdateInstaller()
        self.programs = []
    
    def scan_programs(self, force_rescan=False):
        """Scan for installed programs"""
        if not self.programs or force_rescan:
            print(f"{Fore.BLUE}Scanning for installed programs...{Style.RESET_ALL}")
            self.programs = self.detector.scan_installed_programs()
            print(f"{Fore.GREEN}Found {len(self.programs)} installed programs{Style.RESET_ALL}")
        return self.programs
    
    def check_updates(self):
        """Check for available updates"""
        if not self.programs:
            self.scan_programs()
        
        print(f"{Fore.BLUE}Checking for updates...{Style.RESET_ALL}")
        self.programs = self.checker.check_for_updates(self.programs)
        
        updates_available = [p for p in self.programs if p.update_available]
        print(f"{Fore.GREEN}Found {len(updates_available)} programs with available updates{Style.RESET_ALL}")
        
        return updates_available
    
    def list_programs(self, show_updates_only=False):
        """List installed programs"""
        if not self.programs:
            self.scan_programs()
        
        programs_to_show = self.programs
        if show_updates_only:
            programs_to_show = [p for p in self.programs if p.update_available]
        
        if not programs_to_show:
            print(f"{Fore.YELLOW}No programs found{Style.RESET_ALL}")
            return
        
        # Prepare table data
        headers = ["Name", "Current Version", "Available Version", "Source", "Update Available"]
        rows = []
        
        for program in programs_to_show:
            update_status = f"{Fore.GREEN}Yes{Style.RESET_ALL}" if program.update_available else f"{Fore.RED}No{Style.RESET_ALL}"
            available_version = program.available_version if program.update_available else "-"
            
            rows.append([
                program.name[:50] + "..." if len(program.name) > 50 else program.name,
                program.version[:20] + "..." if len(program.version) > 20 else program.version,
                available_version[:20] + "..." if len(available_version) > 20 else available_version,
                program.source,
                update_status
            ])
        
        print(f"\n{Fore.CYAN}Installed Programs:{Style.RESET_ALL}")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    def update_all(self, interactive=True):
        """Update all programs with available updates"""
        updates_available = self.check_updates()
        
        if not updates_available:
            print(f"{Fore.YELLOW}No updates available{Style.RESET_ALL}")
            return
        
        # Show what will be updated
        print(f"\n{Fore.CYAN}Programs to be updated:{Style.RESET_ALL}")
        for program in updates_available:
            print(f"  • {program.name} ({program.version} → {program.available_version})")
        
        if interactive and self.config.get('update_behavior.require_confirmation', True):
            response = input(f"\n{Fore.YELLOW}Proceed with updates? (y/N): {Style.RESET_ALL}")
            if response.lower() != 'y':
                print(f"{Fore.YELLOW}Update cancelled{Style.RESET_ALL}")
                return
        
        # Install updates
        print(f"\n{Fore.BLUE}Installing updates...{Style.RESET_ALL}")
        
        def progress_callback(program_name, success, completed, total):
            status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if success else f"{Fore.RED}✗{Style.RESET_ALL}"
            print(f"  {status} {program_name} ({completed}/{total})")
        
        results = self.installer.install_updates(updates_available, progress_callback)
        
        # Show summary
        self._show_update_summary(results)
        
    def update_program(self, program_name: str):
        """Update a specific program"""
        if not self.programs:
            self.scan_programs()
        
        # Find the program
        program = None
        for p in self.programs:
            if program_name.lower() in p.name.lower():
                program = p
                break
        
        if not program:
            print(f"{Fore.RED}Program '{program_name}' not found{Style.RESET_ALL}")
            return
        
        # Check if update is available
        self.programs = self.checker.check_for_updates([program])
        program = self.programs[0]  # Get updated program info
        
        if not program.update_available:
            print(f"{Fore.YELLOW}No update available for {program.name}{Style.RESET_ALL}")
            return
        
        print(f"{Fore.BLUE}Updating {program.name}...{Style.RESET_ALL}")
        result = self.installer.install_single_program(program)
        
        if result.success:
            print(f"{Fore.GREEN}✓ Successfully updated {program.name}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Failed to update {program.name}: {result.error_message}{Style.RESET_ALL}")
    
    def _show_update_summary(self, results: dict):
        """Show summary of update results"""
        successful = sum(1 for r in results.values() if r.success)
        failed = len(results) - successful
        
        print(f"\n{Fore.CYAN}Update Summary:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}Successful: {successful}{Style.RESET_ALL}")
        print(f"  {Fore.RED}Failed: {failed}{Style.RESET_ALL}")
        
        if failed > 0:
            print(f"\n{Fore.RED}Failed Updates:{Style.RESET_ALL}")
            for name, result in results.items():
                if not result.success:
                    print(f"  • {name}: {result.error_message}")
    
    def export_program_list(self, filename: str = None):
        """Export program list to JSON file"""
        if not self.programs:
            self.scan_programs()
        
        if not filename:
            filename = f"programs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = []
        for program in self.programs:
            export_data.append({
                'name': program.name,
                'version': program.version,
                'publisher': program.publisher,
                'source': program.source,
                'package_id': program.package_id,
                'update_available': program.update_available,
                'available_version': program.available_version
            })
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print(f"{Fore.GREEN}Program list exported to {filename}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Failed to export program list: {e}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(
        description="Windows Patch Manager - Manage software updates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python patch_manager.py --scan                    # Scan for programs
  python patch_manager.py --check-updates           # Check for updates
  python patch_manager.py --list                    # List all programs
  python patch_manager.py --list-updates            # List programs with updates
  python patch_manager.py --update-all              # Update all programs
  python patch_manager.py --update "Chrome"         # Update specific program
  python patch_manager.py --export programs.json    # Export program list
        """
    )
    
    parser.add_argument('--scan', action='store_true', help='Scan for installed programs')
    parser.add_argument('--check-updates', action='store_true', help='Check for available updates')
    parser.add_argument('--list', action='store_true', help='List all installed programs')
    parser.add_argument('--list-updates', action='store_true', help='List programs with available updates')
    parser.add_argument('--update-all', action='store_true', help='Update all programs with available updates')
    parser.add_argument('--update', metavar='PROGRAM', help='Update specific program')
    parser.add_argument('--export', metavar='FILE', nargs='?', const='programs.json', help='Export program list to JSON')
    parser.add_argument('--config', action='store_true', help='Show configuration file location')
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    # Handle no arguments - show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    try:
        pm = PatchManager()
        
        # Override confirmation setting if --no-confirm
        if args.no_confirm:
            pm.config.set('update_behavior.require_confirmation', False)
        
        if args.config:
            config_path = Path('config.json').absolute()
            print(f"Configuration file: {config_path}")
            if config_path.exists():
                print(f"{Fore.GREEN}File exists{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}File will be created on first run{Style.RESET_ALL}")
        
        elif args.scan:
            pm.scan_programs(force_rescan=True)
        
        elif args.check_updates:
            pm.check_updates()
        
        elif args.list:
            pm.list_programs()
        
        elif args.list_updates:
            pm.list_programs(show_updates_only=True)
        
        elif args.update_all:
            pm.update_all(interactive=not args.no_confirm)
        
        elif args.update:
            pm.update_program(args.update)
        
        elif args.export:
            pm.export_program_list(args.export)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
