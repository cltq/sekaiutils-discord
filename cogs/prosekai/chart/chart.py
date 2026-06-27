import logging
import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_builder import EmbedBuilder

log = logging.getLogger(__name__)

API_BASE = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main"

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

DIFFICULTY_ORDER = ["easy", "normal", "hard", "expert", "master", "append"]


class Chart(commands.Cog):
    __cog_name__ = "Chart"

    def __init__(self, bot):
        self.bot = bot

    async def _fetch_data(self) -> tuple[list[dict], dict[int, list[dict]]]:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/musics.json", timeout=aiohttp.ClientTimeout(total=30)) as r:
                musics = await r.json()
            async with session.get(f"{API_BASE}/musicDifficulties.json", timeout=aiohttp.ClientTimeout(total=30)) as r:
                diffs = await r.json()
        by_music: dict[int, list[dict]] = {}
        for d in diffs:
            by_music.setdefault(d["musicId"], []).append(d)
        return musics, by_music

    async def _suggest_songs(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        try:
            musics, _ = await self._fetch_data()
        except Exception:
            return [app_commands.Choice(name="ไม่สามารถโหลดรายชื่อเพลงได้", value="")]

        matches = [s for s in musics if current.lower() in s.get("title", "").lower()]
        matches.sort(key=lambda s: s.get("title", ""))

        return [
            app_commands.Choice(name=s["title"], value=str(s["id"]))
            for s in matches[:25]
        ]

    @discord.app_commands.command(name="chart", description="ค้นหา chart เพลงใน Project Sekai")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(
        song="ชื่อเพลงหรือเลือกจากรายการ",
        difficulty="ระดับ difficulty (easy / normal / hard / expert / master / append)",
    )
    @app_commands.autocomplete(song=_suggest_songs)
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
            musics, diff_map = await self._fetch_data()
        except Exception as e:
            log.error("Failed to fetch chart data: %s", e)
            await interaction.followup.send(
                "ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ข้อมูลเพลงได้ กรุณาลองใหม่ภายหลัง",
                ephemeral=True,
            )
            return

        matched = next((s for s in musics if str(s.get("id")) == song), None)
        if not matched:
            matched = next((s for s in musics if song.lower() in s.get("title", "").lower()), None)

        if not matched:
            await interaction.followup.send(
                f"ไม่พบเพลงที่ตรงกับ \"{song}\"",
                ephemeral=True,
            )
            return

        charts = diff_map.get(matched["id"], [])

        if difficulty:
            c = next((d for d in charts if d["musicDifficulty"] == difficulty), None)
            if not c:
                await interaction.followup.send(
                    f"ไม่พบ chart {DIFFICULTIES.get(difficulty, difficulty)} สำหรับเพลง \"{matched['title']}\"",
                    ephemeral=True,
                )
                return
            self._show_chart(interaction, matched, c)
        else:
            self._show_song(interaction, matched, charts)

    def _show_song(self, interaction: discord.Interaction, song: dict, charts: list[dict]):
        title = song.get("title", "(ไม่ทราบชื่อ)")
        composer = song.get("composer", "(ไม่ทราบผู้แต่ง)")
        categories = song.get("categories", ["original"])
        category = categories[0] if categories else "original"

        embed = EmbedBuilder.hex("#FF66AA", f"🎵 {title}")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        embed.add_inline_field("ผู้แต่ง", composer, inline=False)

        seen = set()
        for d in sorted(charts, key=lambda x: DIFFICULTY_ORDER.index(x["musicDifficulty"]) if x["musicDifficulty"] in DIFFICULTY_ORDER else 99):
            diff = d["musicDifficulty"]
            if diff in seen:
                continue
            seen.add(diff)
            level = d.get("playLevel", "?")
            notes = d.get("totalNoteCount", "?")
            color = DIFFICULTY_COLORS.get(diff, "#FFFFFF")
            embed.add_inline_field(
                f"{DIFFICULTIES.get(diff, diff).upper()} ★{level}",
                f"โน้ต: {notes}",
            )

        embed.add_inline_field("หมวดหมู่", category, inline=False)
        interaction.followup.send(embed=embed, ephemeral=True)

    def _show_chart(self, interaction: discord.Interaction, song: dict, chart: dict):
        diff = chart["musicDifficulty"]
        title = song.get("title", "(ไม่ทราบชื่อ)")
        level = chart.get("playLevel", "?")
        notes = chart.get("totalNoteCount", "?")
        color = DIFFICULTY_COLORS.get(diff, "#FFFFFF")
        label = DIFFICULTIES.get(diff, diff.upper())

        embed = EmbedBuilder.hex(color, f"🎵 {title} — {label} ★{level}")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        embed.add_inline_field("โน้ตทั้งหมด", str(notes))

        interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Chart(bot))
