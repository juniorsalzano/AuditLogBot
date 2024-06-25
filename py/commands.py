import discord
from discord.ext import commands
import json
import os

# Define the file path for storing ignored user IDs
IGNORED_USERS_FILE = 'scripts/ignored_users.json'

# Load ignored user IDs from the JSON file
def load_ignored_users():
    if os.path.isfile(IGNORED_USERS_FILE):
        with open(IGNORED_USERS_FILE, 'r') as file:
            return json.load(file)
    return []

# Save ignored user IDs to the JSON file
def save_ignored_users():
    with open(IGNORED_USERS_FILE, 'w') as file:
        json.dump(ignored_users, file)

# List to store ignored user IDs
ignored_users = load_ignored_users()

def setup(bot):
    @bot.command()
    async def ignore(ctx, user: discord.User):
        if user.id not in ignored_users:
            ignored_users.append(user.id)
            save_ignored_users()
            await ctx.send(f"Ignoring audit logs from {user.mention}.")
        else:
            await ctx.send(f"{user.mention} is already ignored.")

    @bot.command()
    async def unignore(ctx, user: discord.User):
        if user.id in ignored_users:
            ignored_users.remove(user.id)
            save_ignored_users()
            await ctx.send(f"Stopped ignoring audit logs from {user.mention}.")
        else:
            await ctx.send(f"{user.mention} is not currently ignored.")

    @bot.command()
    async def list(ctx):
        if ignored_users:
            ignored_mentions = [ctx.guild.get_member(user_id).mention for user_id in ignored_users if ctx.guild.get_member(user_id)]
            await ctx.send("Ignored users:\n" + "\n".join(ignored_mentions))
        else:
            await ctx.send("No users are currently ignored.")
