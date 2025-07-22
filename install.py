#!/usr/bin/env python3
"""
Windows Patch Manager Installer
Sets up the patch manager environment and dependencies.
"""

import sys
import subprocess
import os
from pathlib import Path
import requests
import zipfile
import tempfile

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python from https://python.org")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_admin_privileges():
    """Check if running with administrator privileges"""
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            print("✅ Running with administrator privileges")
        else:
            print("⚠️  Not running as administrator")
            print("   Some features may require elevated privileges")
        return is_admin
    except:
        print("⚠️  Could not determine privilege level")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"   Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def check_winget():
    """Check if Windows Package Manager is available"""
    try:
        result = subprocess.run(
            ["winget", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Windows Package Manager found: {version}")
            return True
        else:
            print("⚠️  Windows Package Manager not responding")
            return False
            
    except FileNotFoundError:
        print("❌ Windows Package Manager (winget) not found")
        print("   Please install from Microsoft Store or GitHub:")
        print("   https://github.com/microsoft/winget-cli/releases")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Windows Package Manager check timed out")
        return False

def check_chocolatey():
    """Check if Chocolatey is available"""
    try:
        result = subprocess.run(
            ["choco", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Chocolatey found: {version}")
            return True
        else:
            print("ℹ️  Chocolatey not responding")
            return False
            
    except FileNotFoundError:
        print("ℹ️  Chocolatey not found (optional)")
        print("   Install from: https://chocolatey.org/install")
        return False
    except subprocess.TimeoutExpired:
        print("ℹ️  Chocolatey check timed out")
        return False

def create_shortcuts():
    """Create desktop shortcuts"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        script_dir = Path(__file__).parent.absolute()
        
        # GUI shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(Path(desktop) / "Patch Manager.lnk"))
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{script_dir / "gui.py"}"'
        shortcut.WorkingDirectory = str(script_dir)
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print("✅ Desktop shortcuts created")
        return True
        
    except ImportError:
        print("ℹ️  Cannot create shortcuts (pywin32 not available)")
        return False
    except Exception as e:
        print(f"⚠️  Could not create shortcuts: {e}")
        return False

def setup_config():
    """Set up initial configuration"""
    config_file = Path("config.json")
    
    if config_file.exists():
        print("ℹ️  Configuration file already exists")
        return True
    
    try:
        # Import and create config
        from config_manager import get_config
        config = get_config()
        print("✅ Configuration file created")
        return True
    except Exception as e:
        print(f"⚠️  Could not create configuration: {e}")
        return False

def run_initial_scan():
    """Run initial program scan"""
    print("🔍 Running initial program scan...")
    
    try:
        result = subprocess.run([
            sys.executable, "patch_manager.py", "--scan", "--verbose"
        ], timeout=120)
        
        if result.returncode == 0:
            print("✅ Initial scan completed")
            return True
        else:
            print("⚠️  Initial scan had issues")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Initial scan timed out")
        return False
    except Exception as e:
        print(f"⚠️  Could not run initial scan: {e}")
        return False

def main():
    print("🚀 Windows Patch Manager Installer")
    print("==================================")
    print()
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    check_admin_privileges()
    print()
    
    # Install dependencies
    if not install_dependencies():
        return 1
    print()
    
    # Check external tools
    winget_available = check_winget()
    choco_available = check_chocolatey()
    print()
    
    if not winget_available and not choco_available:
        print("⚠️  Warning: No package managers found")
        print("   The patch manager will have limited functionality")
        print("   Please install winget (recommended) or Chocolatey")
        print()
    
    # Setup configuration
    setup_config()
    
    # Create shortcuts
    create_shortcuts()
    
    # Run initial scan
    print()
    response = input("🔍 Run initial program scan now? (Y/n): ")
    if response.lower() != 'n':
        run_initial_scan()
    
    print()
    print("🎉 Installation completed!")
    print()
    print("Usage:")
    print("  • Run 'run.bat' or '.\run.ps1' to launch GUI (recommended)")
    print("  • Run 'python gui.py' for graphical interface")
    print("  • Run 'python patch_manager.py --help' for command line usage")
    print("  • Check desktop for shortcuts")
    print()
    print("Next steps:")
    print("  • Review config.json for settings")
    print("  • Set up scheduled updates: python scheduler.py create")
    print("  • Run your first update check via GUI or: python patch_manager.py --check-updates")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
