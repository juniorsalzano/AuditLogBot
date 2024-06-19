import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import asyncio

load_dotenv()

TOKEN = os.getenv('TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
AUDIT_LOG_PREFIX = "[Audit Log]"

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.members = True
intents.guild_messages = True
intents.guild_reactions = True
intents.typing = False
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def print_audit_log(entry):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        time_format = "%Y-%m-%d %H:%M:%S"
        timestamp = entry.created_at.strftime(time_format)
        username = entry.user.name
        action = entry.action
        target = entry.target
        
        user_avatar_url = entry.user.avatar.url if entry.user.avatar else entry.user.default_avatar.url  # Get user's avatar URL or default avatar URL
        user_profile_url = f"https://discord.com/users/{entry.user.id}"  # Construct user profile URL
        
        embed = discord.Embed(
            title="Audit Log",
            description=f"User: [{username}]({user_profile_url})\n"  # Make username clickable
                        f"Time: {timestamp}\n"
                        f"Entry action: {action}\n"
                        f"Target action: {target}",
            color=discord.Color.blue()
        )
        
        embed.set_thumbnail(url=user_avatar_url)  # Set user's avatar as thumbnail
        embed.set_footer(text="Audit Log Notification")
        
        await channel.send(embed=embed)

@bot.event
async def on_ready():
    print('Bot is ready.')
    bot.loop.create_task(on_guild_audit_log_task())

async def on_guild_audit_log_task():
    last_entries = []
    while True:
        guild = bot.guilds[0]
        new_entries = await get_audit_logs(guild, limit=1)
        if new_entries:
            if new_entries[0] not in last_entries:
                last_entries.append(new_entries[0])
                await print_audit_log(new_entries[0])
        await asyncio.sleep(10)  # Wait for 10 seconds before checking for new entries

async def get_audit_logs(guild, limit=None):
    audit_logs = guild.audit_logs(limit=limit)
    entries = []
    async for entry in audit_logs:
        entries.append(entry)
    return entries

bot.run(TOKEN)
