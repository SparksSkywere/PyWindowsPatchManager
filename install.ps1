# Windows Patch Manager GUI Installer
# Sets up the patch manager environment and dependencies with a graphical interface

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Hide PowerShell console window
Add-Type -Name Window -Namespace Console -MemberDefinition '
[DllImport("Kernel32.dll")]
public static extern IntPtr GetConsoleWindow();

[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
'

$consolePtr = [Console.Window]::GetConsoleWindow()
# Hide window (0 = SW_HIDE)
[Console.Window]::ShowWindow($consolePtr, 0)

# Get script directory and set install location
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$installDir = "$env:APPDATA\skywereindustries\WindowsPatchManager"
$version = "1.0.0"
$displayName = "Windows Patch Manager"

# Global variables for GUI components
$form = $null
$statusLabel = $null
$progressBar = $null
$logTextBox = $null
$installButton = $null
$exitButton = $null

# Function to log messages to GUI
function Write-Log {
    param([string]$message, [string]$color = "Black")
    
    if ($logTextBox) {
        $logTextBox.SelectionStart = $logTextBox.TextLength
        $logTextBox.SelectionLength = 0
        $logTextBox.SelectionColor = [System.Drawing.Color]::FromName($color)
        $logTextBox.AppendText("$message`r`n")
        $logTextBox.ScrollToCaret()
        $form.Update()
    }
}

# Function to update status
function Update-Status {
    param([string]$message)
    
    if ($statusLabel) {
        $statusLabel.Text = $message
        $form.Update()
    }
}

# Function to update progress
function Update-Progress {
    param([int]$value)
    
    if ($progressBar) {
        $progressBar.Value = [Math]::Min([Math]::Max($value, 0), 100)
        $form.Update()
    }
}

# Function to copy files to AppData
function Copy-InstallFiles {
    Update-Status "Copying files to installation directory..."
    Write-Log "Creating installation directory: $installDir" "Blue"
    
    try {
        # Create install directory
        if (-not (Test-Path $installDir)) {
            New-Item -Path $installDir -ItemType Directory -Force | Out-Null
        }
        
        # Copy all Python files and dependencies
        $filesToCopy = @(
            "*.py",
            "*.ps1", 
            "*.txt",
            "*.json",
            "*.md"
        )
        
        foreach ($pattern in $filesToCopy) {
            $files = Get-ChildItem -Path $scriptDir -Filter $pattern -File
            foreach ($file in $files) {
                Copy-Item -Path $file.FullName -Destination $installDir -Force
                Write-Log "Copied: $($file.Name)" "Gray"
            }
        }
        
        Write-Log "SUCCESS: Files copied to $installDir" "Green"
        return $true
    }
    catch {
        Write-Log "ERROR: Failed to copy files: $($_.Exception.Message)" "Red"
        return $false
    }
}

# Function to create uninstaller
function Create-Uninstaller {
    Update-Status "Creating uninstaller..."
    Write-Log "Creating uninstaller script..." "Blue"
    
    try {
        $uninstallScript = @"
# Windows Patch Manager Uninstaller
Add-Type -AssemblyName System.Windows.Forms

# Hide PowerShell console window
Add-Type -Name Window -Namespace Console -MemberDefinition '
[DllImport("Kernel32.dll")]
public static extern IntPtr GetConsoleWindow();

[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
'

`$consolePtr = [Console.Window]::GetConsoleWindow()
[Console.Window]::ShowWindow(`$consolePtr, 0)

`$result = [System.Windows.Forms.MessageBox]::Show(
    "Are you sure you want to uninstall Windows Patch Manager?`n`nThis will remove all program files and registry entries.",
    "Uninstall Windows Patch Manager",
    [System.Windows.Forms.MessageBoxButtons]::YesNo,
    [System.Windows.Forms.MessageBoxIcon]::Question
)

if (`$result -eq [System.Windows.Forms.DialogResult]::Yes) {
    try {
        # Remove desktop shortcut
        `$desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
        `$shortcut = "`$desktop\Patch Manager.lnk"
        if (Test-Path `$shortcut) {
            Remove-Item `$shortcut -Force
        }
        
        # Remove registry entry
        `$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\WindowsPatchManager"
        if (Test-Path `$regPath) {
            Remove-Item `$regPath -Recurse -Force
        }
        
        # Remove installation directory (schedule for deletion on reboot if needed)
        `$installDir = "$installDir"
        if (Test-Path `$installDir) {
            try {
                Remove-Item `$installDir -Recurse -Force
            } catch {
                # If files are in use, schedule for deletion on reboot
                Get-ChildItem `$installDir -Recurse | ForEach-Object {
                    if (`$_.PSIsContainer -eq `$false) {
                        try {
                            Remove-Item `$_.FullName -Force
                        } catch {
                            # Schedule file for deletion on reboot
                        }
                    }
                }
            }
        }
        
        [System.Windows.Forms.MessageBox]::Show(
            "Windows Patch Manager has been successfully uninstalled.",
            "Uninstall Complete",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Information
        )
    }
    catch {
        [System.Windows.Forms.MessageBox]::Show(
            "An error occurred during uninstallation: `$(`$_.Exception.Message)",
            "Uninstall Error",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        )
    }
}
"@
        
        $uninstallScript | Out-File -FilePath "$installDir\uninstall.ps1" -Encoding UTF8
        Write-Log "SUCCESS: Uninstaller created" "Green"
        return $true
    }
    catch {
        Write-Log "WARNING: Could not create uninstaller: $($_.Exception.Message)" "Orange"
        return $false
    }
}

# Function to register in Programs and Features
function Register-InProgramsAndFeatures {
    Update-Status "Registering in Programs and Features..."
    Write-Log "Adding entry to Programs and Features..." "Blue"
    
    try {
        $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\WindowsPatchManager"
        
        # Create registry key
        New-Item -Path $regPath -Force | Out-Null
        
        # Set registry values
        Set-ItemProperty -Path $regPath -Name "DisplayName" -Value $displayName
        Set-ItemProperty -Path $regPath -Name "DisplayVersion" -Value $version
        Set-ItemProperty -Path $regPath -Name "Publisher" -Value "skywereindustries"
        Set-ItemProperty -Path $regPath -Name "InstallLocation" -Value $installDir
        Set-ItemProperty -Path $regPath -Name "UninstallString" -Value "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$installDir\uninstall.ps1`""
        Set-ItemProperty -Path $regPath -Name "QuietUninstallString" -Value "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$installDir\uninstall.ps1`""
        Set-ItemProperty -Path $regPath -Name "NoModify" -Value 1 -Type DWord
        Set-ItemProperty -Path $regPath -Name "NoRepair" -Value 1 -Type DWord
        Set-ItemProperty -Path $regPath -Name "EstimatedSize" -Value 5000 -Type DWord  # Size in KB
        
        $installDate = Get-Date -Format "yyyyMMdd"
        Set-ItemProperty -Path $regPath -Name "InstallDate" -Value $installDate
        
        Write-Log "SUCCESS: Registered in Programs and Features" "Green"
        return $true
    }
    catch {
        Write-Log "WARNING: Could not register in Programs and Features: $($_.Exception.Message)" "Orange"
        return $false
    }
}
function Test-PythonVersion {
    Update-Status "Checking Python version..."
    Write-Log "Checking Python installation..." "Blue"
    
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        
        $versionMatch = $pythonVersion -match "Python (\d+\.\d+\.\d+)"
        if (-not $versionMatch) {
            throw "Could not parse Python version"
        }
        
        $version = [Version]$matches[1]
        $minVersion = [Version]"3.8.0"
        
        if ($version -lt $minVersion) {
            Write-Log "ERROR: Python 3.8 or higher is required" "Red"
            Write-Log "Current version: $pythonVersion" "Red"
            Write-Log "Please upgrade Python from https://python.org" "Red"
            return $false
        }
        
        Write-Log "SUCCESS: Python $($version.ToString()) detected" "Green"
        return $true
    }
    catch {
        Write-Log "ERROR: Python is not installed or not in PATH" "Red"
        Write-Log "Please install Python 3.8 or higher from https://python.org" "Red"
        return $false
    }
}

# Function to install Python dependencies
function Install-Dependencies {
    Update-Status "Installing Python dependencies..."
    Write-Log "Installing Python dependencies..." "Blue"
    
    Set-Location $installDir
    
    if (-not (Test-Path "requirements.txt")) {
        Write-Log "ERROR: requirements.txt not found" "Red"
        return $false
    }
    
    try {
        $env:PYTHONDONTWRITEBYTECODE = "1"
        $result = python -m pip install -r requirements.txt 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "SUCCESS: Dependencies installed successfully" "Green"
            return $true
        } else {
            Write-Log "ERROR: Failed to install dependencies" "Red"
            Write-Log "Error: $result" "Red"
            return $false
        }
    }
    catch {
        Write-Log "ERROR: Failed to install dependencies: $($_.Exception.Message)" "Red"
        return $false
    }
}

# Function to check Windows Package Manager (winget)
function Test-Winget {
    Update-Status "Checking Windows Package Manager..."
    Write-Log "Checking Windows Package Manager (winget)..." "Blue"
    
    try {
        $version = winget --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "SUCCESS: Windows Package Manager found: $version" "Green"
            return $true
        } else {
            Write-Log "WARNING: Windows Package Manager not responding" "Orange"
            return $false
        }
    }
    catch {
        Write-Log "WARNING: Windows Package Manager (winget) not found" "Orange"
        Write-Log "Please install from Microsoft Store or GitHub:" "Orange"
        Write-Log "https://github.com/microsoft/winget-cli/releases" "Orange"
        return $false
    }
}

# Function to check Chocolatey
function Test-Chocolatey {
    Update-Status "Checking Chocolatey..."
    Write-Log "Checking Chocolatey..." "Blue"
    
    try {
        $version = choco --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "SUCCESS: Chocolatey found: $version" "Green"
            return $true
        } else {
            Write-Log "INFO: Chocolatey not responding" "Gray"
            return $false
        }
    }
    catch {
        Write-Log "INFO: Chocolatey not found (optional)" "Gray"
        Write-Log "Install from: https://chocolatey.org/install" "Gray"
        return $false
    }
}

# Function to create desktop shortcuts
function New-DesktopShortcuts {
    Update-Status "Creating desktop shortcuts..."
    Write-Log "Creating desktop shortcuts..." "Blue"
    
    try {
        $shell = New-Object -ComObject WScript.Shell
        $desktop = $shell.SpecialFolders("Desktop")
        
        # GUI Shortcut
        $shortcut = $shell.CreateShortcut("$desktop\Patch Manager.lnk")
        $shortcut.TargetPath = "powershell.exe"
        $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$installDir\Patch-Manager.ps1`""
        $shortcut.WorkingDirectory = $installDir
        $shortcut.IconLocation = "powershell.exe,0"
        $shortcut.Description = "Windows Patch Manager GUI"
        $shortcut.Save()
        
        Write-Log "SUCCESS: Desktop shortcuts created" "Green"
        return $true
    }
    catch {
        Write-Log "WARNING: Could not create shortcuts: $($_.Exception.Message)" "Orange"
        return $false
    }
}

# Function to setup configuration
function Initialize-Config {
    Update-Status "Setting up configuration..."
    Write-Log "Setting up configuration..." "Blue"
    
    Set-Location $installDir
    
    if (Test-Path "config.json") {
        Write-Log "INFO: Configuration file already exists" "Gray"
        return $true
    }
    
    try {
        $env:PYTHONDONTWRITEBYTECODE = "1"
        $result = python -c "from config_manager import get_config; get_config()" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "SUCCESS: Configuration file created" "Green"
            return $true
        } else {
            Write-Log "WARNING: Could not create configuration: $result" "Orange"
            return $false
        }
    }
    catch {
        Write-Log "WARNING: Could not create configuration: $($_.Exception.Message)" "Orange"
        return $false
    }
}

# Function to run installation process
function Start-Installation {
    $installButton.Enabled = $false
    $exitButton.Text = "Close"
    Update-Progress 0
    
    Write-Log "Starting Windows Patch Manager installation..." "Blue"
    Write-Log "Running with administrator privileges" "Green"
    Write-Log "Installing to: $installDir" "Blue"
    
    # Copy files to AppData
    Update-Progress 5
    if (-not (Copy-InstallFiles)) {
        Write-Log "Installation failed - Could not copy files" "Red"
        $installButton.Enabled = $true
        $installButton.Text = "Retry Installation"
        return
    }
    
    # Check Python version
    Update-Progress 15
    if (-not (Test-PythonVersion)) {
        Write-Log "Installation failed - Python requirements not met" "Red"
        $installButton.Enabled = $true
        $installButton.Text = "Retry Installation"
        return
    }
    
    # Install dependencies
    Update-Progress 35
    if (-not (Install-Dependencies)) {
        Write-Log "Installation failed - Could not install dependencies" "Red"
        $installButton.Enabled = $true
        $installButton.Text = "Retry Installation"
        return
    }
    
    # Check external tools
    Update-Progress 50
    $wingetAvailable = Test-Winget
    Update-Progress 55
    $chocoAvailable = Test-Chocolatey
    
    if (-not $wingetAvailable -and -not $chocoAvailable) {
        Write-Log "WARNING: No package managers found" "Orange"
        Write-Log "The patch manager will have limited functionality" "Orange"
        Write-Log "Please install winget (recommended) or Chocolatey" "Orange"
    }
    
    # Setup configuration
    Update-Progress 65
    Initialize-Config
    
    # Create uninstaller
    Update-Progress 75
    Create-Uninstaller
    
    # Register in Programs and Features
    Update-Progress 80
    Register-InProgramsAndFeatures
    
    # Create shortcuts
    Update-Progress 95
    New-DesktopShortcuts
    
    Update-Progress 100
    Update-Status "Installation completed successfully!"
    Write-Log "" "Black"
    Write-Log "Installation completed!" "Green"
    Write-Log "" "Black"
    Write-Log "Installation Location: $installDir" "Blue"
    Write-Log "" "Black"
    Write-Log "Usage:" "Blue"
    Write-Log "Double-click the desktop shortcut 'Patch Manager'" "Black"
    Write-Log "Run programs can be found in Settings > Apps" "Black"
    Write-Log "Uninstall via Settings > Apps or Control Panel" "Black"
    Write-Log "" "Black"
    Write-Log "Next steps:" "Blue"
    Write-Log "Review config.json for settings" "Black"
    Write-Log "Run your first update check via GUI" "Black"
    
    $installButton.Text = "Installation Complete"
}

# Create main form
function Create-InstallerGUI {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Windows Patch Manager - Installer"
    $form.Size = New-Object System.Drawing.Size(700, 500)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    
    # Title label
    $titleLabel = New-Object System.Windows.Forms.Label
    $titleLabel.Text = "Windows Patch Manager Installer"
    $titleLabel.Font = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)
    $titleLabel.Location = New-Object System.Drawing.Point(20, 20)
    $titleLabel.Size = New-Object System.Drawing.Size(400, 25)
    $form.Controls.Add($titleLabel)
    
    # Description label
    $descLabel = New-Object System.Windows.Forms.Label
    $descLabel.Text = "This installer will set up the Windows Patch Manager environment and dependencies."
    $descLabel.Location = New-Object System.Drawing.Point(20, 50)
    $descLabel.Size = New-Object System.Drawing.Size(650, 20)
    $form.Controls.Add($descLabel)
    
    # Status label
    $script:statusLabel = New-Object System.Windows.Forms.Label
    $statusLabel.Text = "Ready to install"
    $statusLabel.Location = New-Object System.Drawing.Point(20, 80)
    $statusLabel.Size = New-Object System.Drawing.Size(500, 20)
    $form.Controls.Add($statusLabel)
    
    # Progress bar
    $script:progressBar = New-Object System.Windows.Forms.ProgressBar
    $progressBar.Location = New-Object System.Drawing.Point(20, 105)
    $progressBar.Size = New-Object System.Drawing.Size(650, 20)
    $progressBar.Value = 0
    $form.Controls.Add($progressBar)
    
    # Log text box
    $script:logTextBox = New-Object System.Windows.Forms.RichTextBox
    $logTextBox.Location = New-Object System.Drawing.Point(20, 135)
    $logTextBox.Size = New-Object System.Drawing.Size(650, 250)
    $logTextBox.ReadOnly = $true
    $logTextBox.Font = New-Object System.Drawing.Font("Consolas", 9)
    $logTextBox.BackColor = [System.Drawing.Color]::White
    $form.Controls.Add($logTextBox)
    
    # Install button
    $script:installButton = New-Object System.Windows.Forms.Button
    $installButton.Text = "Start Installation"
    $installButton.Location = New-Object System.Drawing.Point(480, 430)
    $installButton.Size = New-Object System.Drawing.Size(120, 30)
    $installButton.BackColor = [System.Drawing.Color]::LightGreen
    $installButton.Add_Click({ Start-Installation })
    $form.Controls.Add($installButton)
    
    # Exit button
    $script:exitButton = New-Object System.Windows.Forms.Button
    $exitButton.Text = "Exit"
    $exitButton.Location = New-Object System.Drawing.Point(610, 430)
    $exitButton.Size = New-Object System.Drawing.Size(60, 30)
    $exitButton.Add_Click({ $form.Close() })
    $form.Controls.Add($exitButton)
    
    # Set form reference globally
    $script:form = $form
    
    # Show the form
    $form.ShowDialog()
}

# Start the GUI installer
Create-InstallerGUI
