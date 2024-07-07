### File Descriptions:
JewFuss-XT.pyw: the code for the RAT (.pyw extension makes the console not show when opening the file, usually you would use send the exe which dose not require installing anything)

`requirements.txt`: all the libraries that need to be installed to run the raw python file (can install all at the same time using `pip install -r requirements.txt`)

`/source/JewFuss-XT.template.py`: the file that `easy-compiler.py` uses to build from

`/builds/easy-compiler-build.log`: the build log (builds saved in same folder)

`/data`: the folder holding temporary data (doesn't delete, allowing for it to build faster, i dont know how it works because i didnt create pyinstaller)

`depreciated compile.py`: **(DEPRECIATED)** compiles the `JewFuss-XT.pyw` file, bot token is entered into the code manually here, use this if you are going to use the same token repeatitivly, good for testing

`easy-compiler.py` (recommended): compiles from `/source/JewFuss-XT.template.py`, prompts you for discord token instead, works by getting the contents of the file, creating a temporary copy, finding a line containing the string `# Do not remove this string (easy compiler looks for this) - 23r98h` with somthing like `TOKEN = "MTE3ODQyMzE0Njc4OTk5ODY4NQ.GgkE0m.-o1d8MDaIhMZiH5j11CKiqMNTgM0ERvGkznwNA"`

`LICENSE`: MIT License under Gabrielzv1233

`.gitignore`: Tells GIT what to not upload