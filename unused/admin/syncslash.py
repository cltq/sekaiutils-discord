import discord
from discord.ext import commands
from utils.admin_guard import admin_check


class SyncSlash(commands.Cog):
    @discord.app_commands.command(name="syncslash", description="Re-synchronize all slash commands")
    @admin_check()
    async def sync_slash(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.client.tree.sync()
        await interaction.edit_original_response(content="Slash commands synced.")


async def setup(bot):
    await bot.add_cog(SyncSlash())
