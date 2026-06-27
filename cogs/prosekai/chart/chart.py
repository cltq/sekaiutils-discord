import logging
import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_builder import EmbedBuilder

log = logging.getLogger(__name__)

API_BASE = "https://sekai.best/api/v2"

DIFFICULTIES = {
    "easy": "EASY",
    "normal": "NORMAL",
    "hard": "HARD",
    "expert": "EXPERT",
    "master": "MASTER",
    "append": "APPEND",
}

DIFFICULTY_COLORS = {
    "easy": "#22CC44",
    "normal": "#FFCC00",
    "hard": "#FF8800",
    "expert": "#FF2244",
    "master": "#CC44FF",
    "append": "#FF66AA",
}


class Chart(commands.Cog):
    __cog_name__ = "Chart"

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="chart", description="ค้นหา chart เพลงใน Project Sekai")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(
        song="ชื่อเพลงหรือบางส่วนของชื่อเพลงที่ต้องการค้นหา",
        difficulty="ระดับ difficulty (easy / normal / hard / expert / master / append)",
    )
    @app_commands.choices(difficulty=[
        app_commands.Choice(name="EASY", value="easy"),
        app_commands.Choice(name="NORMAL", value="normal"),
        app_commands.Choice(name="HARD", value="hard"),
        app_commands.Choice(name="EXPERT", value="expert"),
        app_commands.Choice(name="MASTER", value="master"),
        app_commands.Choice(name="APPEND", value="append"),
    ])
    async def chart(
        self,
        interaction: discord.Interaction,
        song: str,
        difficulty: str | None = None,
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            songs = await self._fetch_songs()
        except Exception:
            await interaction.followup.send(
                "ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ข้อมูลเพลงได้ กรุณาลองใหม่ภายหลัง",
                ephemeral=True,
            )
            return

        matches = [s for s in songs if song.lower() in s.get("title", "").lower()]

        if not matches:
            await interaction.followup.send(
                f"ไม่พบเพลงที่ชื่อ \"{song}\"",
                ephemeral=True,
            )
            return

        matched = matches[0]

        if difficulty:
            charts = [c for c in matched.get("charts", []) if c.get("difficulty") == difficulty]
            if not charts:
                await interaction.followup.send(
                    f"ไม่พบ chart {DIFFICULTIES.get(difficulty, difficulty)} สำหรับเพลง \"{matched['title']}\"",
                    ephemeral=True,
                )
                return
            self._show_chart(interaction, matched, charts[0], difficulty)
        else:
            self._show_song(interaction, matched)

    def _show_song(self, interaction: discord.Interaction, song: dict):
        title = song.get("title", "(ไม่ทราบชื่อ)")
        artist = song.get("composer", song.get("artist", "(ไม่ทราบผู้แต่ง)"))
        category = song.get("categories", [None])[0] or "original"
        embed = EmbedBuilder.hex("#FF66AA", f"🎵 {title}")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        embed.add_inline_field("ศิลปิน", artist, inline=False)

        for chart in song.get("charts", []):
            diff = chart.get("difficulty", "?")
            level = chart.get("level", "?")
            note_count = sum(chart.get("noteCounts", {}).values()) if "noteCounts" in chart else "?"
            color = DIFFICULTY_COLORS.get(diff, "#FFFFFF")
            embed.add_inline_field(
                f"{DIFFICULTIES.get(diff, diff).upper()} ★{level}",
                f"โน้ต: {note_count}",
            )

        embed.add_inline_field("หมวดหมู่", category, inline=False)
        interaction.followup.send(embed=embed, ephemeral=True)

    def _show_chart(self, interaction: discord.Interaction, song: dict, chart: dict, diff_key: str):
        title = song.get("title", "(ไม่ทราบชื่อ)")
        level = chart.get("level", "?")
        note_counts = chart.get("noteCounts", {})
        total_notes = sum(note_counts.values())
        color = DIFFICULTY_COLORS.get(diff_key, "#FFFFFF")
        diff_label = DIFFICULTIES.get(diff_key, diff_key.upper())

        embed = EmbedBuilder.hex(color, f"🎵 {title} — {diff_label} ★{level}")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        embed.add_inline_field("โน้ตทั้งหมด", str(total_notes))

        for note_type, count in note_counts.items():
            embed.add_inline_field(note_type.capitalize(), str(count))

        embed.add_inline_field("Combo", str(chart.get("combo", "?")), inline=False)

        interaction.followup.send(embed=embed, ephemeral=True)

    async def _fetch_songs(self) -> list[dict]:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/songs", timeout=aiohttp.ClientTimeout(total=20)) as resp:
                data = await resp.json()
                return data.get("songs", data) if isinstance(data, dict) else data


async def setup(bot):
    await bot.add_cog(Chart(bot))
