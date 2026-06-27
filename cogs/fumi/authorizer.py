import os
import discord
from discord.ext import commands
from discord import app_commands


class Authorizer(commands.Cog):
    __cog_name__ = "Authorizer"

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="auth", description="รับลิงก์ยืนยันตัวตนสำหรับเชื่อมต่อบอทเซไก")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(secret_key="รหัสลับสำหรับยืนยันตัวตน")
    async def auth(self, interaction: discord.Interaction, secret_key: str):
        expected = os.environ.get("DISCORD_CMD_AUTH_SK", "")
        if secret_key != expected:
            await interaction.response.send_message(
                "รหัสลับไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง",
                ephemeral=True,
            )
            return

        link = os.environ.get("DISCORD_BOT_OA2_LINK", "")
        if not link:
            await interaction.response.send_message(
                "ไม่พบลิงก์ยืนยันตัวตนในระบบ โปรดแจ้งผู้ดูแล",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"ลิงก์ยืนยันตัวตนของคุณ: {link}",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Authorizer(bot))
