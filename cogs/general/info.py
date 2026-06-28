import os
import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_builder import EmbedBuilder

PRIMARY = "#5865F2"


class Info(commands.Cog):
    __cog_name__ = "ข้อมูลบอท"

    def __init__(self, bot):
        self.bot = bot
        self.start_time = discord.utils.utcnow()

    def _uptime(self) -> str:
        delta = discord.utils.utcnow() - self.start_time
        days = delta.days
        hours, rem = divmod(delta.seconds, 3600)
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

    def _owner_id(self) -> str | None:
        return os.environ.get("BOT_CREATOR")

    @discord.app_commands.command(name="info", description="แสดงข้อมูลบอท")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def info(self, interaction: discord.Interaction):
        owner_id = self._owner_id()
        owner_mention = f"<@{owner_id}>" if owner_id else "ไม่ทราบ"

        embed = EmbedBuilder.hex(PRIMARY, "ข้อมูลบอท", f"ข้อมูลทั่วไปของ {self.bot.user.name}")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_inline_field("ชื่อ", self.bot.user.name)
        embed.add_inline_field("ID", str(self.bot.user.id))
        embed.add_inline_field("เจ้าของ", owner_mention)
        embed.add_inline_field("อัปไทม์", self._uptime())
        embed.add_inline_field("Status Page", "https://discordstatus.com")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
