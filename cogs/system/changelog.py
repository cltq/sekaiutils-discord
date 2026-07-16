import re
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from utils.embed_builder import EmbedBuilder

PRIMARY = "#5865F2"
CHANGELOG_DIR = Path(__file__).resolve().parents[2] / "changelogs"

FILENAME_RE = re.compile(r"changelog-(\d{4}-\d{2}-\d{2})-(\d{2}-\d{2})\.md$", re.IGNORECASE)


def _parse_changelogs() -> list[tuple[str, str, Path]]:
    results = []
    if not CHANGELOG_DIR.is_dir():
        return results
    for f in sorted(CHANGELOG_DIR.glob("changelog-*.md"), reverse=True):
        m = FILENAME_RE.match(f.name)
        if m:
            date_str, time_str = m.group(1), m.group(2)
            results.append((date_str, time_str, f))
    return results


def _read_changelog(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return "(ไม่สามารถอ่านไฟล์ได้)"


def _truncate(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


class Changelog(commands.Cog):
    __cog_name__ = "System"

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="changelog", description="ดู changelog ล่าสุดหรือเลือกดูตามวันที่")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(select="เลือกวันที่ changelog (ถ้าไม่เลือกจะแสดงตัวล่าสุด)")
    async def changelog(self, interaction: discord.Interaction, select: str | None = None):
        await interaction.response.defer(ephemeral=True, thinking=True)

        changelogs = _parse_changelogs()
        if not changelogs:
            embed = EmbedBuilder.warning("Changelog", "ยังไม่มี changelog ในระบบ")
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if select:
            target = None
            for date_str, time_str, path in changelogs:
                if f"{date_str}-{time_str}" in select or date_str in select:
                    target = (date_str, time_str, path)
                    break
            if not target:
                embed = EmbedBuilder.error("Changelog", f"ไม่พบ changelog สำหรับ `{select}`")
                embed.set_footer(text=f"Requested by {interaction.user.display_name}")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            date_str, time_str, path = target
        else:
            date_str, time_str, path = changelogs[0]

        content = _read_changelog(path)
        display_date = f"{date_str} {time_str}"

        embed = EmbedBuilder.hex(PRIMARY, f"📋 Changelog — {display_date}", _truncate(content))
        embed.set_footer(text=f"ไฟล์: {path.name} • Requested by {interaction.user.display_name}")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @changelog.autocomplete("select")
    async def changelog_autocomplete(self, interaction: discord.Interaction, current: str):
        changelogs = _parse_changelogs()
        choices = []
        for date_str, time_str, _ in changelogs:
            label = f"{date_str} {time_str}"
            if current and current.lower() not in label.lower():
                continue
            choices.append(app_commands.Choice(name=label, value=label))
            if len(choices) >= 25:
                break
        return choices


async def setup(bot):
    await bot.add_cog(Changelog(bot))
