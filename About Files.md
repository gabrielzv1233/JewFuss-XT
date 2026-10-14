# File Descriptions:
`JewFuss-XT.py`: The source code `easy-compiler.py` & `easy-compiler-ui.py` builds into an executable

`easy-compiler-ui.py`: The prefered compiler, complete with features not found in `easy-compiler.py`

`installer.py`: A payload installer with a built in self-compiler, bundling JewFuss-XT into the executable. Requests elevation and creates a startup task automatically. Used when updating via the `$update` command.

`LICENSE`: MIT License under Gabrielzv1233

`requirements.txt`: Python package dependencies, may be installed using `pip install -r requirements.txt`

`/builds/easy-compiler-build.log`: A log updated after a sucessful compile (builds are also saved in same folder)

`/data/`: A folder containing the build files (Deleting this may increase duration of the next build)

`.gitignore`: Tells Git what to not upload

# Unmaintained files
`pullupdates.py`: A script to update the project using git. WARNING: this will overwrite changes if you have made any. I also don't update this
`easy-compiler.py`: Compiles from `JewFuss-XT.py`, automatically fills the TOKEN variable and compiles using pyinstaller  
`JewFuss-Lite.py`: A dumbed down version of JewFuss-XT
`/exebundler/`: A project intended to inject the installer into another exectable