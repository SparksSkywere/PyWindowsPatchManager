# Windows Patch Manager

A Python-based tool for managing software updates on Windows. Automatically detects installed programs and updates them using winget and Chocolatey.

## Installation

1. Download this repository
2. Right-click `install.ps1` and run as powershell
3. The installer will set up everything automatically

## Usage

**Launch the GUI:**
- Double-click the "Patch Manager" desktop shortcut

**Command Line:**
```bash
python patch_manager.py --scan
python patch_manager.py --update-all
```

## Requirements

- Windows 10/11
- Python 3.8+
- Windows Package Manager (winget) recommended