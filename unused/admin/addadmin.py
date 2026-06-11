import discord
from discord.ext import commands
from utils.admin_guard import admin_check, add_to_allowlist


class AddAdmin(commands.Cog):
    @discord.app_commands.command(name="addadmin", description="Add a user to the admin allowlist")
    @admin_check()
    async def add_admin(self, interaction: discord.Interaction, user: discord.User):
        added = add_to_allowlist(str(interaction.guild_id), str(user.id), user.name)
        if not added:
            await interaction.response.send_message(
                "That user is already in the allowlist.", ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"Added **{user}** to the admin allowlist.", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(AddAdmin())
