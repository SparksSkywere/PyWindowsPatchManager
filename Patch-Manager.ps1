# Windows Patch Manager GUI Launcher
# Launches the GUI silently without showing console window

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

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Change to script directory
Set-Location $scriptDir

# Check if Python is available (silently)
try {
    $null = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
}
catch {
    # Show error dialog if Python is not found
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show("Python is not installed or not in PATH.`n`nPlease install Python 3.8 or higher from https://python.org", "Windows Patch Manager - Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    exit 1
}

# Launch GUI silently (pythonw hides console for Python scripts)
try {
    if (Get-Command pythonw -ErrorAction SilentlyContinue) {
        Start-Process -FilePath "pythonw" -ArgumentList "gui.py" -WorkingDirectory $scriptDir -WindowStyle Hidden
    } else {
        Start-Process -FilePath "python" -ArgumentList "gui.py" -WorkingDirectory $scriptDir -WindowStyle Hidden
    }
}
catch {
    # Show error dialog if GUI launch fails
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show("Failed to launch Windows Patch Manager GUI.`n`nError: $($_.Exception.Message)", "Windows Patch Manager - Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    exit 1
}
