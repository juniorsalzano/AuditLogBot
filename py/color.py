import discord

def get_embed_color(action):
    action_colors = {
        discord.AuditLogAction.message_delete: discord.Color.red(),
        discord.AuditLogAction.message_bulk_delete: discord.Color.dark_red(),
        discord.AuditLogAction.message_pin: discord.Color.blue(),
        discord.AuditLogAction.message_unpin: discord.Color.dark_blue(),
        discord.AuditLogAction.role_create: discord.Color.green(),
        discord.AuditLogAction.role_update: discord.Color.orange(),
        discord.AuditLogAction.role_delete: discord.Color.dark_orange(),
        discord.AuditLogAction.kick: discord.Color.magenta(),
        discord.AuditLogAction.ban: discord.Color.dark_red(),
        discord.AuditLogAction.unban: discord.Color.dark_green(),
        discord.AuditLogAction.member_update: discord.Color.purple(),
        discord.AuditLogAction.member_role_update: discord.Color.dark_orange(),
        discord.AuditLogAction.channel_create: discord.Color.teal(),
        discord.AuditLogAction.channel_update: discord.Color.gold(),
        discord.AuditLogAction.channel_delete: discord.Color.dark_blue(),
        discord.AuditLogAction.guild_update: discord.Color.light_grey(),
        # Add more actions and their colors here
    }
    return action_colors.get(action, discord.Color.default())
