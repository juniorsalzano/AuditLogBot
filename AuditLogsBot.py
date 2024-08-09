import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import asyncio
import json
import logging
from py.commands import setup as commands_setup
from py.utils import print_audit_log, make_avatar_round
from py.custom_help import setup as help_setup
import psutil

load_dotenv()

# Set up logging
log_file_path = 'bot.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord')

TOKEN = os.getenv('TOKEN')

# Load multiple channel IDs from environment variables
CHANNEL_IDS = list(map(int, os.getenv('CHANNEL_IDS').split(',')))

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
    logger.info('Bot is ready.')
    if not on_guild_audit_log_task.is_running():
        on_guild_audit_log_task.start()
    if not monitor_resources.is_running():
        monitor_resources.start()

@tasks.loop(seconds=1)
async def on_guild_audit_log_task():
    await bot.wait_until_ready()
    last_entry_id = None
    guild = bot.guilds[0]

    while True:
        try:
            new_entries = await get_audit_logs(guild, limit=1)
            if new_entries:
                new_entry = new_entries[0]
                if new_entry.id != last_entry_id:
                    await send_audit_logs_to_channels(new_entry, bot, CHANNEL_IDS, config)
                    last_entry_id = new_entry.id
        except Exception as e:
            logger.error(f"Error fetching audit logs: {e}")

        await asyncio.sleep(1)  # Wait for 1 second before checking for new entries

async def send_audit_logs_to_channels(entry, bot, channel_ids, config):
    for channel_id in channel_ids:
        channel = bot.get_channel(channel_id)
        if channel:
            await print_audit_log(entry, bot, channel_id, config)
        else:
            logger.warning(f"Channel ID {channel_id} not found.")

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
                logger.warning(f"Discord server error, retrying... ({retries} retries left)")
                await asyncio.sleep(delay)
            else:
                raise
        except Exception as e:
            logger.error(f"Unexpected error fetching audit logs: {e}")
            raise
    raise Exception("Failed to fetch audit logs after multiple retries")

@tasks.loop(seconds=1)
async def monitor_resources():
    # Monitor CPU and memory usage
    process = psutil.Process(os.getpid())
    cpu_usage = psutil.cpu_percent(interval=None)
    memory_usage = process.memory_info().rss / 1024 / 1024  # Convert to MB

    if cpu_usage > 1.0 or memory_usage > 75:
        logger.info(f"CPU usage: {cpu_usage}%")
        logger.info(f"Memory usage: {memory_usage:.2f} MB")

commands_setup(bot)
help_setup(bot)  # Set up the custom help command

bot.run(TOKEN)