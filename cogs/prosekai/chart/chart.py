import logging
import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_builder import EmbedBuilder

log = logging.getLogger(__name__)

JP_BASE = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main"
EN_BASE = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-en-diff/main"

SERVERS = [
    ("🇯🇵 JP", JP_BASE),
    ("🇺🇸 EN", EN_BASE),
]

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

    async def _fetch_server(self, base: str) -> tuple[list[dict], dict[int, list[dict]]]:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base}/musics.json", timeout=aiohttp.ClientTimeout(total=30)) as r:
                musics = await r.json()
            async with session.get(f"{base}/musicDifficulties.json", timeout=aiohttp.ClientTimeout(total=30)) as r:
                diffs = await r.json()
        by_music: dict[int, list[dict]] = {}
        for d in diffs:
            by_music.setdefault(d["musicId"], []).append(d)
        return musics, by_music

    async def _fetch_all(self):
        import asyncio
        results = await asyncio.gather(
            *(self._fetch_server(base) for _, base in SERVERS),
            return_exceptions=True,
        )
        data = {}
        for (label, _), result in zip(SERVERS, results):
            if isinstance(result, Exception):
                log.error("Failed to fetch %s: %s", label, result)
                data[label] = None
            else:
                data[label] = result
        return data

    def _match_song(self, query: str, server_data: tuple[list[dict], dict[int, list[dict]]] | None):
        if server_data is None:
            return None
        musics, _ = server_data
        matched = next((s for s in musics if str(s.get("id")) == query), None)
        if matched:
            return matched
        q = query.lower()
        matched = next((s for s in musics if q in s.get("title", "").lower()), None)
        if matched:
            return matched
        matched = next((s for s in musics if q in s.get("pronunciation", "").lower()), None)
        return matched

    async def _suggest_songs(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        try:
            all_data = await self._fetch_all()
        except Exception:
            return [app_commands.Choice(name="ไม่สามารถโหลดรายชื่อเพลงได้", value="")]

        seen_ids: set[int] = set()
        suggestions: list[app_commands.Choice[str]] = []
        q = current.lower()

        for label in ("🇯🇵 JP", "🇺🇸 EN"):
            pair = all_data.get(label)
            if pair is None:
                continue
            musics, _ = pair
            for s in musics:
                sid = s["id"]
                if sid in seen_ids:
                    continue
                title = s.get("title", "")
                pron = s.get("pronunciation", "")
                if q in title.lower() or q in pron.lower():
                    seen_ids.add(sid)
                    tag = "🇯🇵" if label == "🇯🇵 JP" else "🇺🇸"
                    suggestions.append(app_commands.Choice(name=f"{tag} {title}", value=str(sid)))
                    if len(suggestions) >= 25:
                        break
            if len(suggestions) >= 25:
                break

        return suggestions[:25]

    @discord.app_commands.command(name="chart", description="ค้นหา chart เพลงใน Project Sekai (JP / EN)")
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

        all_data = await self._fetch_all()

        matched_song = None
        matched_label = None
        for label in ("🇯🇵 JP", "🇺🇸 EN"):
            s = self._match_song(song, all_data.get(label))
            if s is not None:
                matched_song = s
                matched_label = label
                break

        if matched_song is None:
            await interaction.followup.send(
                f"ไม่พบเพลงที่ตรงกับ \"{song}\"",
                ephemeral=True,
            )
            return

        presence = []
        jp_data = all_data.get("🇯🇵 JP")
        en_data = all_data.get("🇺🇸 EN")
        jp_has = jp_data is not None and any(str(s["id"]) == str(matched_song["id"]) for s in jp_data[0])
        en_has = en_data is not None and any(str(s["id"]) == str(matched_song["id"]) for s in en_data[0])
        if jp_has:
            presence.append("🇯🇵 JP")
        if en_has:
            presence.append("🇺🇸 EN")
        presence_str = " / ".join(presence) if presence else matched_label

        _, diff_map = all_data.get(matched_label, (None, {}))
        charts = diff_map.get(matched_song["id"], [])

        if difficulty:
            c = next((d for d in charts if d["musicDifficulty"] == difficulty), None)
            if not c:
                await interaction.followup.send(
                    f"ไม่พบ chart {DIFFICULTIES.get(difficulty, difficulty)} สำหรับเพลง \"{matched_song['title']}\"",
                    ephemeral=True,
                )
                return
            self._show_chart(interaction, matched_song, c, presence_str)
        else:
            self._show_song(interaction, matched_song, charts, presence_str)

    def _show_song(self, interaction: discord.Interaction, song: dict, charts: list[dict], server: str):
        title = song.get("title", "(ไม่ทราบชื่อ)")
        composer = song.get("composer", "(ไม่ทราบผู้แต่ง)")
        categories = song.get("categories", ["original"])
        category = categories[0] if categories else "original"

        embed = EmbedBuilder.hex("#FF66AA", f"🎵 {title}")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        embed.add_inline_field("ผู้แต่ง", composer, inline=False)
        embed.add_inline_field("เซิร์ฟเวอร์", server, inline=False)

        seen = set()
        for d in sorted(charts, key=lambda x: DIFFICULTY_ORDER.index(x["musicDifficulty"]) if x["musicDifficulty"] in DIFFICULTY_ORDER else 99):
            diff = d["musicDifficulty"]
            if diff in seen:
                continue
            seen.add(diff)
            level = d.get("playLevel", "?")
            notes = d.get("totalNoteCount", "?")
            embed.add_inline_field(
                f"{DIFFICULTIES.get(diff, diff).upper()} ★{level}",
                f"โน้ต: {notes}",
            )

        embed.add_inline_field("หมวดหมู่", category, inline=False)
        interaction.followup.send(embed=embed, ephemeral=True)

    def _show_chart(self, interaction: discord.Interaction, song: dict, chart: dict, server: str):
        diff = chart["musicDifficulty"]
        title = song.get("title", "(ไม่ทราบชื่อ)")
        level = chart.get("playLevel", "?")
        notes = chart.get("totalNoteCount", "?")
        color = DIFFICULTY_COLORS.get(diff, "#FFFFFF")
        label = DIFFICULTIES.get(diff, diff.upper())

        embed = EmbedBuilder.hex(color, f"🎵 {title} — {label} ★{level}")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        embed.add_inline_field("เซิร์ฟเวอร์", server, inline=False)
        embed.add_inline_field("โน้ตทั้งหมด", str(notes))

        interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Chart(bot))
