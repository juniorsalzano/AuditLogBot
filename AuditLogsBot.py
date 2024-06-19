import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import json
from datetime import timedelta
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from commands import setup as commands_setup, ignored_users

load_dotenv()

TOKEN = os.getenv('TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Load configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.members = True
intents.guild_messages = True
intents.guild_reactions = True
intents.typing = False
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)

def make_avatar_round(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    size = (128, 128)
    img = img.resize(size, Image.LANCZOS)
    
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    img.putalpha(mask)

    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return discord.File(fp=output, filename="avatar.png")

async def print_audit_log(entry):
    # Check if the user is in the ignored list
    if entry.user.id in ignored_users:
        return

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        time_format = "%Y-%m-%d %H:%M:%S"
        original_timestamp = discord.utils.snowflake_time(entry.id)
        
        # Adjust the timestamp using the timezone offset from config.json
        timezone_offset = config.get('timezone_offset', 0)
        adjusted_timestamp = original_timestamp + timedelta(hours=timezone_offset)
        
        timestamp = adjusted_timestamp.strftime(time_format)
        action = entry.action
        target = entry.target
        changes = entry.changes if entry.changes else "No changes"
        
        # Get user's avatar URL or default avatar URL
        user_avatar_url = entry.user.avatar.url if entry.user.avatar else entry.user.default_avatar.url
        user_mention = entry.user.mention  # Mention the user (@username)
        
        file = make_avatar_round(user_avatar_url)

        embed = discord.Embed(
            title="Audit Log",
            description=(
                f"User: {user_mention}\n"
                f"Time: {timestamp} UTC {timezone_offset:+}\n"
                f"Entry action: {action}\n"
                f"Target action: {target}\n"
                f"Changes: \n{changes}\n"
            ),
            color=discord.Color.from_rgb(config['color']['audit_log']['r'], config['color']['audit_log']['g'], config['color']['audit_log']['b'])
        )
        
        embed.set_thumbnail(url="attachment://avatar.png")  # Set user's avatar as thumbnail
        
        await channel.send(embed=embed, file=file)

@bot.event
async def on_ready():
    print('Bot is ready.')
    bot.loop.create_task(on_guild_audit_log_task())

async def on_guild_audit_log_task():
    last_entry_id = None
    while True:
        guild = bot.guilds[0]
        new_entries = await get_audit_logs(guild, limit=1)
        if new_entries:
            new_entry = new_entries[0]
            if new_entry.id != last_entry_id:
                await print_audit_log(new_entry)
                last_entry_id = new_entry.id
        await asyncio.sleep(1)  # Wait for 1 second before checking for new entries

async def get_audit_logs(guild, limit=None):
    audit_logs = guild.audit_logs(limit=limit)
    entries = []
    async for entry in audit_logs:
        entries.append(entry)
    return entries

commands_setup(bot)
bot.run(TOKEN)
