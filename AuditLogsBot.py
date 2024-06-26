import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import json
from py.commands import setup as commands_setup  # Import the setup function and ignored_users list
from py.utils import print_audit_log, make_avatar_round  # Import utility functions
from py.custom_help import setup as help_setup  # Import custom help command setup

load_dotenv()

TOKEN = os.getenv('TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Load configuration from config.json
with open('scripts/config.json', 'r') as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.members = True
intents.guild_messages = True
intents.guild_reactions = True
intents.typing = False
intents.message_content = True

bot = commands.Bot(command_prefix='&', intents=intents)

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
                await print_audit_log(new_entry, bot, CHANNEL_ID, config)
                last_entry_id = new_entry.id
        await asyncio.sleep(3)  # Wait for 3 seconds before checking for new entries

async def get_audit_logs(guild, limit=None, retries=3, delay=5):
    while retries > 0:
        try:
            audit_logs = guild.audit_logs(limit=limit)
            entries = []
            async for entry in audit_logs:
                entries.append(entry)
            return entries
        except discord.errors.DiscordServerError as e:
            if e.status == 503:
                retries -= 1
                await asyncio.sleep(delay)
            else:
                raise
    raise Exception("Failed to fetch audit logs after multiple retries")

commands_setup(bot)
help_setup(bot)  # Set up the custom help command

bot.run(TOKEN)
