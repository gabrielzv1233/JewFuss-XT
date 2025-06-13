from tkinter import filedialog
from pathlib import Path
import argparse
import tempfile
import win32api
import win32con
import win32gui
import win32ui
import shutil
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, 'builds')
data_dir = os.path.join(base_dir, 'data')
os.makedirs(data_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

def extract_icon(exe_path, data_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')):
    if not exe_path:
        raise SystemExit("No EXE selected.")

    large, small = win32gui.ExtractIconEx(exe_path, 0)
    if not large:
        raise Exception("No icon found in EXE.")

    icon_handle = large[0]

    ico_path = os.path.join(data_dir, 'icon.ico')
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0, 0), icon_handle)
    hbmp.SaveBitmapFile(hdc, os.path.join(data_dir, 'temp.bmp'))

    from PIL import Image
    img = Image.open(os.path.join(data_dir, 'temp.bmp'))
    img.save(ico_path, format='ICO')

    os.remove(os.path.join(data_dir, 'temp.bmp'))
    win32gui.DestroyIcon(icon_handle)

print("Select MAIN executable")
main_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
print("Select SECONDARY executable")
secondary_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])

if not main_path or not secondary_path:
    raise SystemExit("Both main and secondary executables must be selected.")

main_name = Path(main_path).stem

parser = argparse.ArgumentParser()
parser.add_argument('--icon', type=str, default=None)
args = parser.parse_args()

if args.icon is not None:
    icon_path = args.icon
else:
    extract_icon(main_path, data_dir)
    icon_path = os.path.join(base_dir, 'data', 'icon.ico')

build_dir = tempfile.mkdtemp()

shutil.copy2(main_path, os.path.join(build_dir, os.path.basename(main_path)))
shutil.copy2(secondary_path, os.path.join(build_dir, os.path.basename(secondary_path)))

meta = {
    "main": os.path.basename(main_path),
    "secondary": os.path.basename(secondary_path)
}
with open(os.path.join(data_dir, 'bundle_meta.json'), 'w') as f:
    json.dump(meta, f)

shutil.copy2(os.path.join(base_dir, 'exebundler.py'), os.path.join(build_dir, 'exebundler.py'))

os.chdir(build_dir)

os.system(
    f'pyinstaller "exebundler.py" '
    f'--onefile --noconsole '
    f'--distpath="{output_dir}" '
    f'--workpath="{data_dir}" '
    f'--specpath="{data_dir}" '
    f'--icon="{icon_path}" '
    f'--add-data "bundle_meta.json;." '
    f'--add-data "{main_path};." '
    f'--add-data "{secondary_path};." '
    f'--name="{main_name}"'
)