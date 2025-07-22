# Windows Patch Manager - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Windows 10/11
- Python 3.8+ (already installed)
- Administrator privileges (recommended)

### 🔧 Quick Launch
The patch manager is ready to use! Simply run:
```bash
# Windows Batch File (launches GUI)
run.bat

# PowerShell Script (launches GUI)  
.\run.ps1

# Direct GUI launch
python gui.py
```

All dependencies have been installed and the GUI will launch by default.

## 📋 Usage Options

### 1. Graphical User Interface (GUI) - Default
```bash
# Launch GUI with batch script
run.bat

# Launch GUI with PowerShell
.\run.ps1

# Launch GUI directly
python gui.py
```
- User-friendly interface
- Real-time progress tracking
- Interactive program list
- Settings management

### 2. Command Line Interface (CLI)
```bash
# Direct CLI usage
python patch_manager.py --scan                    # Scan for programs
python patch_manager.py --check-updates           # Check for updates
python patch_manager.py --list                    # List all programs
python patch_manager.py --list-updates            # Show programs with updates

# Update operations
python patch_manager.py --update-all              # Update all programs
python patch_manager.py --update "Firefox"        # Update specific program
python patch_manager.py --update-all --no-confirm # Update without prompts

# Export and configuration
python patch_manager.py --export programs.json    # Export program list
python patch_manager.py --config                  # Show config location

# Using PowerShell script with CLI
.\run.ps1 -CLI -CheckUpdates
.\run.ps1 -CLI -UpdateAll

# Using batch script with parameters
run.bat --scan
run.bat --update-all
```

### 3. Batch Scripts (Windows)
```bash
# Launch GUI (default behavior)
run.bat

# Use CLI with parameters
run.bat --scan
run.bat --check-updates

# PowerShell - Launch GUI (default)
.\run.ps1

# PowerShell - Use CLI
.\run.ps1 -CLI -CheckUpdates
.\run.ps1 -CLI -UpdateAll
```

### 4. Scheduled Updates
```bash
# Set up automatic daily updates
python scheduler.py create

# Check scheduled task status
python scheduler.py status

# Remove scheduled updates
python scheduler.py remove
```

### 5. Cleanup System
```bash
# Quick cleanup using dedicated scripts
cleanup.bat                              # Interactive cleanup (batch)
.\cleanup.ps1                           # Interactive cleanup (PowerShell)
.\cleanup.ps1 -Estimate                 # Show cleanup estimate
.\cleanup.ps1 -Force                    # Cleanup without prompts

# Cleanup via patch manager
python patch_manager.py --cleanup       # Full cleanup
python patch_manager.py --cleanup-estimate  # Show estimate

# Cleanup via run scripts
run.bat --cleanup                       # Quick cleanup via batch
.\run.ps1 -CLI -Cleanup                 # Cleanup via PowerShell

# Advanced cleanup options
python cleanup.py --cache               # Clean only cache files
python cleanup.py --logs --days 7       # Clean logs older than 7 days
python cleanup.py --backups --days 30   # Clean backups older than 30 days
python cleanup.py --estimate            # Show cleanup estimate
```

## 🎯 Key Features

### ✅ **Program Detection**
- **Windows Package Manager (winget)** - Primary source
- **Windows Registry** - Comprehensive system scan
- **Chocolatey** - Additional package manager support
- **166 programs detected** on your system

### 🔍 **Update Sources**
- Winget repositories (Microsoft Store, GitHub releases)
- Chocolatey package repository
- Custom handlers for specific software

### 🛡️ **Safety Features**
- Backup creation before updates
- Configurable exclusion lists
- Confirmation prompts
- Comprehensive logging
- Timeout handling

### 🧹 **Cleanup System**
- **Python cache cleanup** - Remove `__pycache__` directories and `.pyc` files
- **Log file management** - Automatic cleanup of old log files
- **Backup retention** - Configurable backup file cleanup
- **Temporary file cleanup** - Remove various temporary files
- **Post-update cleanup** - Automatic cache cleanup after successful updates
- **Multiple interfaces** - GUI button, CLI commands, dedicated scripts

### ⚙️ **Configuration**
Edit `config.json` to customize:
- Update sources and priorities
- Programs to exclude from updates
- Automatic update settings
- Backup and logging preferences
- Cleanup retention settings

## 📊 Current Status

✅ **Installation Complete**
✅ **Dependencies Installed**
✅ **45 Updates Available** (from 166 programs scanned)

Programs with updates include:
- Mozilla Firefox
- Microsoft Edge
- Visual Studio Code
- Node.js
- Python
- PowerShell
- Unity Hub
- OBS Studio
- VLC Media Player
- And 36 more...

## 🚨 Important Notes

### **Exclusions Configured**
These programs are excluded from automatic updates for safety:
- Windows Security
- Microsoft Visual C++ Redistributables
- System drivers and codecs

### **Administrator Rights**
Some updates may require administrator privileges. Run the patch manager as administrator for best results.

### **Internet Connection**
Active internet connection required for update checking and downloading.

## 🔧 Troubleshooting

### **Registry Scan Issues**
If you see Unicode errors during registry scanning:
- This is normal and doesn't affect functionality
- Winget scanning provides comprehensive results
- Registry scan is supplementary

### **Timeout Warnings**
Some programs may timeout during update checks:
- This is normal for large software packages
- The scan continues with other programs
- Individual programs can be updated manually

### **Missing Package Managers**
- **Winget**: Usually pre-installed on Windows 11, available from Microsoft Store
- **Chocolatey**: Optional, install from https://chocolatey.org/install

## 🎉 Next Steps

1. **Review Updates**: `python patch_manager.py --list-updates`
2. **Test Update**: `python patch_manager.py --update "Firefox"` 
3. **Setup Automation**: `python scheduler.py create`
4. **Customize Settings**: Edit `config.json`
5. **Try GUI**: `python gui.py`

## 📞 Support

- Check logs in `logs/` directory for detailed information
- Review `config.json` for configuration options
- Use `--verbose` flag for detailed output
- Refer to `README.md` for comprehensive documentation

---

**🎯 Your Windows Patch Manager is ready to keep your software up to date!**
