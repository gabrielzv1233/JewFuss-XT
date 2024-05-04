# Requirements
- Python installation required (latest version recommended as this is built on it).
- Pyinstaller installation required: `pip install pyinstaller`.

### Running Without Compiling
- To run JewFuss-XT without compiling, Please install all the required extension from requirements.txt using command `pip install -r requirements.txt` and follow the normal setup steps (not steps for easy compiler) than run the script

# Info/Warnings
- running the compiler for the first time will likely take a while, antivirus will also likly block the file when its compiled for the first time, just allow it through defender or whatever software you use and re-run the compiler
- Commands can be executed in any channel by any user. Place this bot only on private servers with trusted members.
- Only one instance of this bot should be active at a time. Running multiple instances will cause commands to execute on all devices. It's possible to deploy the same bot on multiple Discord servers.
- Compilers and JewFuss-XT are specifically designed for Windows. Linux and MacOS are untested and may not work.

# Instructions
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications/).
2. Click on "New Application" in the top right corner and choose a name.
3. Open the OAuth2 page, scroll down to the OAuth2 URL Generator, select "bot," then scroll further down, choose "Administrator," and finally, click "Copy." Open the copied URL and select the server you want to add the bot to.
4. In the Bot tab on the developer panel enable all "Privileged Gateway Intents", than select "Reset Token" and click the copy button.
5. Set the variable TOKEN to your bot token (the one you just copied). If you're using the easy compiler, simply run the script and paste your bot token in the console.
6. In CMD (or your preferred terminal), navigate to the root project folder (where you see this file `readme.md`) and run `python easy-compiler.py` or `python compile.py`. The executable will be saved in the subdirectory `/dist`.
7. (Optional) I recommend running the bot on your device to ensure it works. To stop the bot, type `$estop` in the Discord server where you added the bot, or run `taskkill /im "taskname.exe" /f`, where "taskname.exe" is the name of the executable.

Original source code: [Desu23's JewFuss-X](https://github.com/DeSu23/JewFuss-X/)
