# Requirements
- Python installation required (latest version recommended as this is built on it).
- Pyinstaller installation required: `pip install pyinstaller`.

### Running Without Compiling
- To run JewFuss-XT without compiling, Please install all the required extension from requirements.txt using command `pip install -r requirements.txt` and follow the normal setup steps (not steps for easy compiler) than run the script

# Info/Warnings
- Normal compiler is depreciated hense why its named `depreciated compile.py`
- Running the compiler for the first time will likely take a while, antivirus will also likly block the file when its compiled for the first time, just allow it through your antivirus software and re-run the compiler
- Commands can be executed in any channel by any user. Place this bot only on private servers with trusted members.
- Only one instance of this bot should be active at a time. Running multiple instances will cause commands to execute on all devices. It's possible to deploy the same bot on multiple Discord servers.
- Compilers and JewFuss-XT are specifically designed for Windows. Linux and MacOS are untested and may not work.

# Instructions
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications/).
2. Click on "New Application" in the top right corner and choose a name.
3. Open the OAuth2 page, scroll down to the OAuth2 URL Generator, select "bot," then scroll further down, choose "Administrator," and finally, click "Copy." Open the copied URL and select the server you want to add the bot to.
4. In the Bot tab on the developer panel enable all "Privileged Gateway Intents", than select "Reset Token" and click the copy button.
5. Set the variable TOKEN to your bot token (the one you just copied). If you're using the easy compiler, simply run the script and paste your bot token in the console.
6. In CMD (or your preferred terminal), navigate to the root project folder (where you see this file `readme.md`) and run `python easy-compiler.py` or `python compile.py`. The executable will be saved in the subdirectory `/builds`, old builds will be saved with a timestamp of archive time.
7. (Optional) I recommend running the bot on your device to ensure it works. To stop the bot, type `$estop` in the Discord server where you added the bot, or run `taskkill /im "taskname.exe" /f`, where "taskname.exe" is the name of the executable.

## Where to run commands
Commands are to be ran in their dedicated channel
When JewFuss-XT runs it checks if there is a channel already created, if not it creates a channel
A channel formatted {devicename}-{windowsusername} is created when JewFuss-XT is ran if it does'nt exist already, commands are to be entered here.

## Installer.py
This is kinda complicated, and kinda not, its doucmented in comments at the start of the code but here i go anyway (this is kinda rushed so no special spelling for you)
basically this is a auto installer, it takes care of doing some things for you, simply complie using the provided command
must keep the name `JewFuss-XT.exe` for the jewfuss its bundling, unless you want to change that in the config near the top and also the name of the exe in the pyinstaller command
so what does it do? well simply it creates an exe with jewfuss in it, than it copys it over to the specified path (can also be changed), adds a windows defender exemption, and creates a startup task, and lastly runs it!
so why is this better? well simply, it makes jewfuss run when ANY user logs in, and it runs as admin WITHOUT UAC POPUP
simple warning, dont use the $startup command as it changes the path of jewfuss and breaks it all :\ you can fix it using some effort and the $cmd command tho (really just copy it back to where it was originally, schedule a restart and exit jewfuss, and it should be fine)
i will not lie i have not tested if the scheduled task works, but according to task scheduler, it should

## Final notes 
- Originaly created by desu23 and can be found here [Desu23's JewFuss-X](https://github.com/DeSu23/JewFuss-X/)
- You can submit a github issue if you figure out what causes Windows Defender (or other antivirus's) to trigger 
- If you encoutner any problems when building, make your terminals path is the the same as the easy-compiler's path
- JewFuss-XT is made to be ran on windows and windows only
