import discord
from discord.ext import commands
import json
import os

IGNORED_USERS_FILE = 'scripts/ignored_users.json'
REQUIRED_ROLE_FILE = 'scripts/required_role.json'

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

# Load required role ID from the JSON file
def load_required_role():
    if os.path.isfile(REQUIRED_ROLE_FILE):
        with open(REQUIRED_ROLE_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return None
    return None

# Save required role ID to the JSON file
def save_required_role(role_id):
    with open(REQUIRED_ROLE_FILE, 'w') as file:
        json.dump(role_id, file)

# List to store ignored user IDs
ignored_users = load_ignored_users()
required_role_id = load_required_role()

def role_check():
    async def predicate(ctx):
        if required_role_id is None:
            await ctx.send("The required role for commands has not been set.")
            return False
        required_role = ctx.guild.get_role(required_role_id)
        if required_role in ctx.author.roles:
            return True
        await ctx.send("You do not have the required role to use this command.")
        return False
    return commands.check(predicate)

# Command definitions
@commands.command(help="Sets the required role to use restricted commands. Usage: &setrole @RoleName")
@commands.has_permissions(administrator=True)
async def setrole(ctx, role: discord.Role):
    global required_role_id

    # Check if the role is already set
    if required_role_id is not None:
        required_role = ctx.guild.get_role(required_role_id)
        if required_role in ctx.author.roles:
            required_role_id = role.id
            save_required_role(role.id)
            await ctx.send(f"Required role for commands updated to {role.mention}")
        else:
            await ctx.send("You do not have the required role to update the role.")
    else:
        required_role_id = role.id
        save_required_role(role.id)
        await ctx.send(f"Required role for commands set to {role.mention}")

@commands.command(help="Ignores audit logs from the specified user. Requires the set role. Usage: &ignore @User")
@role_check()
async def ignore(ctx, user: discord.User):
    if user.id not in ignored_users:
        ignored_users.append(user.id)
        save_ignored_users()
        await ctx.send(f"Ignoring audit logs from {user.mention}.")
    else:
        await ctx.send(f"{user.mention} is already ignored.")

@commands.command(help="Stops ignoring audit logs from the specified user. Requires the set role. Usage: &unignore @User")
@role_check()
async def unignore(ctx, user: discord.User):
    if user.id in ignored_users:
        ignored_users.remove(user.id)
        save_ignored_users()
        await ctx.send(f"Stopped ignoring audit logs from {user.mention}.")
    else:
        await ctx.send(f"{user.mention} is not currently ignored.")

@commands.command(help="Lists all users whose audit logs are currently ignored. Requires the set role. Usage: &list")
@role_check()
async def list(ctx):
    if ignored_users:
        ignored_mentions = [ctx.guild.get_member(user_id).mention for user_id in ignored_users if ctx.guild.get_member(user_id)]
        await ctx.send("Ignored users:\n" + "\n".join(ignored_mentions))
    else:
        await ctx.send("No users are currently ignored.")

def setup(bot):
    bot.add_command(setrole)
    bot.add_command(ignore)
    bot.add_command(unignore)
    bot.add_command(list)
