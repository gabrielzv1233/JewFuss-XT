import os
import time
import subprocess

output_dir='./builds'

def rename_file(file_path):
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    new_name = f"{timestamp}-JewFuss-XT.exe"
    new_path = os.path.join(os.path.dirname(file_path), new_name)
    os.rename(file_path, new_path)
    print(f"Renaming JewFuss-XT.exe to {new_name}\n")

file_path = './builds/JewFuss-XT.exe'

if os.path.exists(file_path):
    rename_file(file_path)
elif not os.path.exists(output_dir):
    os.makedirs(output_dir)

subprocess.run(['pyinstaller', 'JewFuss-XT.pyw', '--onefile', '--windowed', '--noconsole', '--distpath=builds', '--workpath=data' , '-n=JewFuss-XT.exe'])
