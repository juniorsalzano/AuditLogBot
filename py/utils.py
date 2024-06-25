import discord
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from datetime import timedelta
from py.color import get_embed_color
from py.commands import ignored_users

async def print_audit_log(entry, bot, channel_id, config):
    # Check if the user is in the ignored list
    if entry.user.id in ignored_users:
        return

    channel = bot.get_channel(channel_id)
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

        color = get_embed_color(action)
        
        embed = discord.Embed(
            title="Audit Log",
            description=(
                f"User: {user_mention}\n"
                f"Time: {timestamp} UTC {timezone_offset:+}\n"
                f"Entry action: {action}\n"
                f"Target action: {target}\n"
                f"Changes: \n{changes}\n"
            ),
            color=color
        )
        
        embed.set_thumbnail(url="attachment://avatar.png")  # Set user's avatar as thumbnail
        
        await channel.send(embed=embed, file=file)

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
