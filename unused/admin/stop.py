import sys
import discord
from discord.ext import commands
from utils.admin_guard import admin_check


class Stop(commands.Cog):
    @discord.app_commands.command(name="stop", description="Stop the bot process")
    @admin_check()
    async def stop(self, interaction: discord.Interaction):
        await interaction.response.send_message("Shutting down...", ephemeral=True)
        sys.exit(0)


async def setup(bot):
    await bot.add_cog(Stop())
