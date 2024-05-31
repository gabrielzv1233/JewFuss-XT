import discord
from discord import app_commands
from discord.ext import commands

TOKEN = "Bot token"

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Running as {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="hello", description="Repeat after me!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is a slash command", ephemeral=True)

@bot.tree.command(name="say", description="Repeat after me!")
@app_commands.describe(say="What do you want me to say?")
async def say(interaction: discord.Interaction, say: str):
    await interaction.response.send_message(say)

bot.run(TOKEN)