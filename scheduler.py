#!/usr/bin/env python3
"""
Windows Patch Manager Scheduler
Sets up automatic update checking and installation.
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

def create_scheduled_task():
    """Create a Windows scheduled task for automatic updates"""
    
    script_dir = Path(__file__).parent.absolute()
    python_exe = sys.executable
    script_path = script_dir / "patch_manager.py"
    
    # Task XML template
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().isoformat()}</Date>
    <Author>Windows Patch Manager</Author>
    <Description>Automatically check and install software updates</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{(datetime.now() + timedelta(hours=1)).isoformat()}</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-32-544</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{script_path}" --check-updates --no-confirm</Arguments>
      <WorkingDirectory>{script_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    
    # Save task XML to temporary file
    temp_xml = script_dir / "patch_manager_task.xml"
    try:
        with open(temp_xml, 'w', encoding='utf-16') as f:
            f.write(task_xml)
        
        # Create the scheduled task
        cmd = [
            "schtasks",
            "/create",
            "/tn", "Windows Patch Manager",
            "/xml", str(temp_xml),
            "/f"  # Force overwrite if exists
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Scheduled task created successfully")
            print("  Task name: Windows Patch Manager")
            print("  Schedule: Daily at current time + 1 hour")
            print("  Action: Check for updates automatically")
        else:
            print(f"✗ Failed to create scheduled task: {result.stderr}")
            return False
        
        # Clean up temporary file
        temp_xml.unlink()
        return True
        
    except Exception as e:
        print(f"✗ Error creating scheduled task: {e}")
        return False

def remove_scheduled_task():
    """Remove the scheduled task"""
    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", "Windows Patch Manager", "/f"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Scheduled task removed successfully")
            return True
        else:
            print(f"✗ Failed to remove scheduled task: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error removing scheduled task: {e}")
        return False

def check_task_status():
    """Check if the scheduled task exists and is enabled"""
    try:
        result = subprocess.run(
            ["schtasks", "/query", "/tn", "Windows Patch Manager", "/fo", "csv"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                # Parse CSV output
                fields = lines[1].split(',')
                if len(fields) >= 4:
                    status = fields[3].strip('"')
                    print(f"✓ Scheduled task exists - Status: {status}")
                    return True
                    
        print("✗ Scheduled task does not exist")
        return False
        
    except Exception as e:
        print(f"✗ Error checking task status: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Windows Patch Manager Scheduler")
        print("================================")
        print()
        print("Usage:")
        print("  python scheduler.py create    # Create scheduled task")
        print("  python scheduler.py remove    # Remove scheduled task")
        print("  python scheduler.py status    # Check task status")
        print("  python scheduler.py run       # Run update check now")
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        print("Creating scheduled task for automatic updates...")
        if create_scheduled_task():
            print()
            print("The task will run daily to check for updates.")
            print("You can modify the schedule using Task Scheduler (taskschd.msc)")
    
    elif command == "remove":
        print("Removing scheduled task...")
        remove_scheduled_task()
    
    elif command == "status":
        print("Checking scheduled task status...")
        check_task_status()
    
    elif command == "run":
        print("Running update check now...")
        script_dir = Path(__file__).parent.absolute()
        script_path = script_dir / "patch_manager.py"
        
        result = subprocess.run([
            sys.executable, str(script_path), "--check-updates", "--no-confirm"
        ], cwd=script_dir)
        
        if result.returncode == 0:
            print("✓ Update check completed")
        else:
            print("✗ Update check failed")
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'create', 'remove', 'status', or 'run'")

if __name__ == "__main__":
    main()
