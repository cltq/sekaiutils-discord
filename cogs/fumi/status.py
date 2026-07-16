import asyncio
import time

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils.embed_builder import EmbedBuilder

MACHINE_IP = "192.168.1.36"
BOT_HEALTHCHECK_PORT = 8899
API_PORT = 6770

PRIMARY = "#5865F2"

STATUS_OK = "🟢"
STATUS_FAIL = "🔴"
STATUS_WARN = "🟡"


class Status(commands.Cog):
    __cog_name__ = "Status"

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
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)

    async def _check_url(self, url: str, timeout: float = 5.0) -> tuple[bool, float]:
        try:
            async with aiohttp.ClientSession() as session:
                start = time.monotonic()
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                    latency = (time.monotonic() - start) * 1000
                    return resp.status < 500, round(latency, 1)
        except Exception:
            return False, 0.0

    @discord.app_commands.command(name="status", description="แสดงสถานะระบบของบอท")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()

        bot_latency = round(self.bot.latency * 1000)
        discord_ok = self.bot.is_ready()

        bot_url = f"http://{MACHINE_IP}:{BOT_HEALTHCHECK_PORT}"
        api_url = f"http://{MACHINE_IP}:{API_PORT}"

        (bot_ok, bot_ms), (api_ok, api_ms) = await asyncio.gather(
            self._check_url(bot_url),
            self._check_url(api_url),
        )

        bot_icon = STATUS_OK if bot_ok else STATUS_FAIL
        api_icon = STATUS_OK if api_ok else STATUS_FAIL
        dc_icon = STATUS_OK if discord_ok else STATUS_FAIL

        embed = EmbedBuilder.hex(PRIMARY, "System Status")

        embed.add_inline_field(
            "Bot Healthcheck",
            f"{bot_icon} `{'UP' if bot_ok else 'DOWN'}`\n"
            f"Latency: `{bot_ms}ms`",
            inline=False,
        )

        embed.add_inline_field(
            "API",
            f"{api_icon} `{'UP' if api_ok else 'DOWN'}`\n"
            f"Latency: `{api_ms}ms`",
            inline=False,
        )

        embed.add_inline_field(
            "Discord API",
            f"{dc_icon} `{'Connected' if discord_ok else 'Disconnected'}`\n"
            f"Latency: `{bot_latency}ms`",
            inline=False,
        )

        embed.add_inline_field(
            "Bot",
            f"Uptime: `{self._format_uptime()}`\n"
            f"Ping: `{bot_latency}ms`",
            inline=False,
        )

        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Status(bot))
