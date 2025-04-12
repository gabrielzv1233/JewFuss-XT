### Requirements
- Python 3.11.9 is recommended. Other versions are untested. PIP is also required.
- Some understanding of how to use Discord bots and a console or IDE.
- A Windows computer to compile the RAT.
- A Windows computer to run the RAT.
- A Discord account.

### Info / Warnings
- **Using a Discord bot to control malware is against the Discord TOS and may result in a ban.**
- **Installing malware on someone else’s computer without their knowledge is ILLEGAL. ONLY USE THIS WITH THE TARGET’S EXPLICIT PERMISSION.**
- Running the compiler for the first time may take a while. Antivirus may also block the file when it’s compiled for the first time — allow it through your antivirus software and re-run the compiler.
- Commands can be executed by any user. Channels and categories created by the bot are set to private by default, so only give trusted Discord members access to them.
- While it's possible to run the same bot on multiple devices, only one instance of this bot should be active at a time. Running multiple instances may cause the bot to get rate-limited. However, it's possible to deploy the same bot to multiple Discord servers.
- The compilers and JewFuss-XT are specifically designed for Windows. Linux and macOS will most likely not work.
- When referencing terminal or your preferred terminal, you can use any app such as PowerShell, CMD, or Terminal.
- Your project root folder is where you’ll find `JewFuss-XT.py`, `easy-compiler.py`, etc.
- Discord rate-limits bots from logging on too frequently. If you get rate-limited, your bot may not be able to come back online for **500 seconds (10 minutes)**.

### Initial Setup
- If you haven’t done so already, click the green **Code** button on GitHub and press **Download ZIP**, then extract the contents to a folder on your PC (this may trigger antivirus).
- Once you have the project files, open the folder in your preferred console and install the required libraries from `requirements.txt` using the command:  
  `pip install -r requirements.txt`
- Follow the instructions in [Bot Setup](#bot-setup) to create a Discord bot to interact with the RAT.

### Bot Setup
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications/).
2. Click **New Application** in the top right corner and choose a name for your bot.
3. Agree to the [Developer Terms of Service](https://support-dev.discord.com/hc/en-us/articles/8562894815383-Discord-Developer-Terms-of-Service) and [Developer Policy](https://support-dev.discord.com/hc/en-us/articles/8563934450327-Discord-Developer-Policy), then press Create (you may be prompted to complete a captcha).
4. In the **Bot** tab, select **Reset Token**, click **Copy**, and save the token somewhere safe. *(Note: Resetting a token requires 2FA if it's enabled on your account.)*
5. Scroll down to **Privileged Gateway Intents** and enable **Presence**, **Server Members**, and **Message Content** intents.

### Compiling the RAT
1. If using a terminal, navigate to the project’s root folder using `cd folderpath` and run `python easy-compiler.py`.  
   If using an IDE like [Visual Studio Code](https://code.visualstudio.com/), open the project folder, open `easy-compiler.py`, and press the **Run** button. *(You may need to configure Python in your IDE first.)*
2. Choose whether to use a custom icon by typing `y` or `n` (`yes` or `no` also work). If you select **yes**, a file chooser will open. If **no**, the default icon will be used.
3. Paste the bot token you saved earlier from the [Bot Setup](#bot-setup) section into the prompt. If the token is invalid, it will ask again.
- The executable will be saved in the `builds` folder. The compiler will automatically open the folder in an Explorer tab with the executable highlighted.
- Old builds are saved with a timestamp of the archive time.
- A log file called `easy-compiler-build.log` will also be created, containing the date of compilation, token used, and the name of the bot.
4. Use the invite link provided by the compiler once it finishes to invite the bot to your Discord server.

### Post Compilation
- To test if the bot works, run the compiled executable. It will take a few seconds to come online, create a channel, and notify you that it's online.  
  You may see errors if the executable is not run as admin (right-click > **Run as administrator**).
- The bot runs as an invisible process (you can see it in Task Manager).  
  To stop it, use `$estop` in Discord or run:  
  `taskkill /im "taskname.exe" /f`  
  Replace `"taskname.exe"` with the executable name (default is `JewFuss-XT.exe`).
- You can see when a user was last online by checking the channel description.

### Where to Run Commands
Commands must be run in their dedicated channel.  
When the bot joins a server or starts, it creates a private category per device, with one channel per user logged on.  
Only people with access to the category/channel or those with admin permissions can access them.  
Admins can run `$init /f` to wipe a channel (delete and recreate it). This does **not** delete categories or other channels.

### Installer.py
`installer.py` is a simple installer. When running the script as `.py`, it compiles itself into an executable.

#### What does it do?
- Copies the bundled executable (the compiled JewFuss-XT) to a target folder.
- Creates a startup task that runs the executable as admin when a user logs in.

The bundled executable is selected during compilation. This should be a valid file in the `builds` folder.  
You can rename `JewFuss-XT.exe` to something like `TotallyNotATrojan.exe`, but the name is case-sensitive, and the installer will check validity.

> ⚠️ **Installer must be run as administrator. Otherwise, it will prompt the user to do so.**

### Updating JewFuss-XT on a Device
This is simple:
- Compile the new version of JewFuss-XT.
- Compile the installer again.
- Run `$upload` in Discord with the compiled installer attached.

**Important:** Use the same executable name as before. If not, it won’t overwrite the current version, and you might end up with **two instances** of JewFuss-XT running (which will execute commands twice).

### Final Notes
- Originally created by **desu23**, see their project [here](https://github.com/DeSu23/JewFuss-X).
- You can submit a GitHub issue if you find what causes Windows Defender (or other antivirus) to flag it.
- If you run into build problems, make sure your terminal's path matches the compiler's path.
- JewFuss-XT is made to run on **Windows only**.