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

@commands.command(help="Displays the last 5 audit logs from the specified user. Usage: &alf @User")
async def alf(ctx, user: discord.User):
    guild = ctx.guild
    audit_logs = []
    async for entry in guild.audit_logs(limit=100):
        if entry.user == user:
            audit_logs.append(entry)

    if audit_logs:
        embed = discord.Embed(title=f"Last 5 Audit Logs for {user}", color=discord.Color.blue())
        for i, entry in enumerate(audit_logs[:5], start=1):  # Get the last 5 entries
            timestamp = discord.utils.snowflake_time(entry.id).strftime("%Y-%m-%d %H:%M:%S")
            action = entry.action
            target = entry.target
            changes = format_audit_log_changes(entry.changes) if entry.changes else "No changes"
            embed.add_field(
                name=f"Audit Log Entry {i} - {timestamp}",
                value=(
                    f"**User:** {user.mention}\n"
                    f"**Action:** {action}\n"
                    f"**Target:** {target}\n"
                    f"**Changes:**\n{changes}\n"
                    f"------"
                ),
                inline=False
            )
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No audit log entries found for {user.mention}.")

def setup(bot):
    bot.add_command(setrole)
    bot.add_command(ignore)
    bot.add_command(unignore)
    bot.add_command(list)
    bot.add_command(alf)

def format_audit_log_changes(changes):
    change_list = []
    attribute_mapping = {
        'name': 'name',
        'type': 'type',
        'nsfw': 'NSFW status',
        'slowmode_delay': 'slowmode delay',
        'overwrites': 'permission overwrites',
        'flags': 'flags',
        'topic': 'topic',
    }
    try:
        before = changes.before
        after = changes.after
        index = 1
        for attr in dir(before):
            if not attr.startswith('_'):
                before_value = getattr(before, attr, None)
                after_value = getattr(after, attr, None)
                if before_value != after_value:  # Only include changes
                    before_str = "None" if before_value is None else str(before_value)
                    after_str = "None" if after_value is None else str(after_value)

                    # Map the attribute to a more readable format if available
                    if attr in attribute_mapping:
                        attr_display = attribute_mapping[attr]
                    else:
                        attr_display = attr.capitalize().replace('_', ' ')

                    if attr == 'type':
                        after_str = 'Text Channel' if after_value == discord.ChannelType.text else str(after_value)

                    change_list.append(f"{index:02d} - **FROM** `{before_str}`\n{index:02d} - **TO** `{after_str}`")
                    index += 1
    except Exception as e:
        change_list.append(f"Error processing changes: {changes}, Error: {e}")
    return "\n".join(change_list)
