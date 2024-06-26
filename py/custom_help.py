import discord
from discord.ext import commands

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", description="List of available commands", color=discord.Color.blue())

        for cog, commands in mapping.items():
            for command in commands:
                if command.help:
                    embed.add_field(name=f"&{command.name}", value=command.help, inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"Help for `{command.name}`", description=command.help or "No description available", color=discord.Color.blue())

        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        embed.add_field(name="Usage", value=self.get_command_signature(command), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title=f"Help for `{cog.qualified_name}`", description=cog.description or "No description available", color=discord.Color.blue())

        for command in cog.get_commands():
            embed.add_field(name=command.name, value=command.help or "No description available", inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=f"Help for `{group.name}` group", description=group.help or "No description available", color=discord.Color.blue())

        for command in group.commands:
            embed.add_field(name=command.name, value=command.help or "No description available", inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

def setup(bot):
    bot.help_command = CustomHelpCommand()
