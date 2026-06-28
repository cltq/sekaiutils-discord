import os
import subprocess
import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_builder import EmbedBuilder

PRIMARY = "#5865F2"
OWNER_WEBSITE = "https://applefumi.xyz"


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

    async def _owner_display(self) -> str:
        owner_id = os.environ.get("BOT_CREATOR")
        if not owner_id:
            return "ไม่ทราบ"
        try:
            user = await self.bot.fetch_user(int(owner_id))
            return user.mention if user else f"`{owner_id}`"
        except Exception:
            return f"`{owner_id}`"

    def _remote_url(self, remote: str) -> str | None:
        try:
            url = subprocess.run(
                ["git", "remote", "get-url", remote],
                capture_output=True, text=True, timeout=10,
            ).stdout.strip()
            if not url:
                return None
            url = url.replace(".git", "")
            if url.startswith("https://"):
                return url
            if ":" in url and "@" in url:
                host = url.split("@")[-1].split(":")[0]
                path = url.split(":")[-1].replace(".git", "")
                return f"https://{host}/{path}"
            return None
        except Exception:
            return None

    @discord.app_commands.command(name="info", description="แสดงข้อมูลบอท")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def info(self, interaction: discord.Interaction):
        owner_display = await self._owner_display()

        gh_url = self._remote_url("origin")
        gitea_url = self._remote_url("gitea")

        embed = EmbedBuilder.hex(PRIMARY, "ข้อมูลบอท", f"ข้อมูลทั่วไปของ {self.bot.user.name}")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_inline_field("ชื่อ", self.bot.user.name, inline=False)
        embed.add_inline_field("ID", str(self.bot.user.id), inline=False)
        embed.add_inline_field("เจ้าของ", owner_display, inline=False)
        embed.add_inline_field("เว็บไซต์", f"[applefumi.xyz]({OWNER_WEBSITE})", inline=False)
        embed.add_inline_field("อัปไทม์", self._uptime(), inline=False)
        embed.add_inline_field("Status Page", "https://discordstatus.com", inline=False)
        if gh_url:
            label = gh_url.split("/", 3)[-1]
            embed.add_inline_field("GitHub", f"[{label}]({gh_url})", inline=False)
        if gitea_url:
            label = gitea_url.split("/", 3)[-1]
            embed.add_inline_field("Gitea", f"[{label}]({gitea_url})", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
