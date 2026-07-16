import os
import time

import discord
from discord import app_commands
from discord.ext import commands

from utils.embed_builder import EmbedBuilder

PRIMARY = "#5865F2"


class Uptime(commands.Cog):
    __cog_name__ = "System"

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.monotonic()

    def _format_uptime(self) -> str:
        delta = time.monotonic() - self.start_time
        days, rem = divmod(int(delta), 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        parts = []
        if days:
            parts.append(f"{days} วัน")
        if hours:
            parts.append(f"{hours} ชั่วโมง")
        if minutes:
            parts.append(f"{minutes} นาที")
        parts.append(f"{seconds} วินาที")
        return " ".join(parts)

    @discord.app_commands.command(name="uptime", description="แสดง uptime ของบอท")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def uptime(self, interaction: discord.Interaction):
        embed = EmbedBuilder.hex(PRIMARY, "⏱ Uptime")
        embed.add_inline_field("อัปไทม์", self._format_uptime(), inline=False)
        embed.add_inline_field("Ping", f"{round(self.bot.latency * 1000)}ms", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="restart", description="รีสตาร์ทบอท (owner only)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def restart(self, interaction: discord.Interaction):
        owner_id = os.environ.get("BOT_CREATOR")
        if str(interaction.user.id) != owner_id:
            embed = EmbedBuilder.error("Restart", "คุณไม่มีสิทธิ์ใช้คำสั่งนี้")
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            await interaction.response.send_message(embed=embed, ephemeral=False)
            return

        embed = EmbedBuilder.success("Restart", "กำลังรีสตาร์ทบอท...")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

        import bot as bot_module
        bot_module.request_restart()
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Uptime(bot))
