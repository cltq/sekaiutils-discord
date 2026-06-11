import os
import sys
import discord
from discord.ext import commands
from utils.admin_guard import admin_check


class Restart(commands.Cog):
    @discord.app_commands.command(name="restart", description="Restart the bot process")
    @admin_check()
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.send_message("Restarting...", ephemeral=True)
        os.execl(sys.executable, sys.executable, *sys.argv)


async def setup(bot):
    await bot.add_cog(Restart())
