# Windows Patch Manager

A comprehensive Python-based patch manager for Windows that can detect and update installed programs (excluding Windows updates).

## Features

- **Graphical User Interface**: Easy-to-use GUI launched by default via run scripts
- **Program Detection**: Automatically scans and detects installed programs
- **Update Checking**: Checks for available updates using multiple sources:
  - Windows Package Manager (winget)
  - Chocolatey (if installed)
  - Custom update checkers for popular software
- **Batch Updates**: Install multiple updates at once
- **Command Line Interface**: Full CLI support for automation and scripting
- **Logging**: Comprehensive logging of all operations
- **Configuration**: Customizable settings for update behavior
- **Exclusion Lists**: Exclude specific programs from updates
- **Scheduling**: Support for scheduled update checks

## Installation

1. Clone this repository or download the source code
2. Install Python 3.8 or higher
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Quick Start (GUI)
```bash
# Windows Batch
run.bat

# PowerShell  
.\run.ps1
```

Both scripts will launch the graphical user interface by default for easy use.

### Command Line Interface
```bash
# Direct CLI usage
python patch_manager.py --scan
python patch_manager.py --update-all

# Using batch script with parameters
run.bat --scan
run.bat --update-all

# Using PowerShell script with CLI flag
.\run.ps1 -CLI -Scan
.\run.ps1 -CLI -UpdateAll
```

### Basic Usage
```bash
python patch_manager.py --scan
python patch_manager.py --update-all
```

### Command Line Options
- `--scan`: Scan for installed programs and available updates
- `--update-all`: Update all programs with available updates
- `--update <program>`: Update a specific program
- `--list-installed`: List all detected installed programs
- `--config`: Open configuration file
- `--verbose`: Enable verbose logging

### Configuration

Edit `config.json` to customize behavior:
- Update sources to use
- Programs to exclude from updates
- Automatic update settings
- Logging preferences

## Requirements

- Windows 10/11
- Python 3.8+
- Administrator privileges (for some operations)
- Windows Package Manager (winget) - recommended

## Supported Update Sources

1. **Windows Package Manager (winget)** - Primary source
2. **Chocolatey** - Secondary source (if installed)
3. **Custom handlers** for specific software

## Safety Features

- Backup creation before updates
- Rollback capability
- Update verification
- Dependency checking

## License

MIT License - See LICENSE file for details
