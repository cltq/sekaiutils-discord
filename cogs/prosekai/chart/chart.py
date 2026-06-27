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

SONGS_PER_PAGE = 20


class Chart(commands.Cog):
    __cog_name__ = "Chart"

    def __init__(self, bot):
        self.bot = bot

    async def _fetch_json(self, url: str, session: aiohttp.ClientSession):
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as r:
            return await r.json(content_type=None)

    async def _fetch_server(self, base: str) -> tuple[list[dict], dict[int, list[dict]]]:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            musics = await self._fetch_json(f"{base}/musics.json", session)
            diffs = await self._fetch_json(f"{base}/musicDifficulties.json", session)
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

    def _build_en_map(self, all_data: dict):
        en_pair = all_data.get("🇺🇸 EN")
        if en_pair is None:
            return {}
        musics, _ = en_pair
        return {s["id"]: s.get("title", "") for s in musics}

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

        en_map = self._build_en_map(all_data)

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
                    en_name = en_map.get(sid)
                    display = f"{title} ({en_name})" if en_name else title
                    tag = "🇯🇵" if label == "🇯🇵 JP" else "🇺🇸"
                    suggestions.append(app_commands.Choice(name=f"{tag} {display}", value=str(sid)))
                    if len(suggestions) >= 25:
                        break
            if len(suggestions) >= 25:
                break

        return suggestions[:25]

    @discord.app_commands.command(name="chart", description="ค้นหา chart เพลงใน Project Sekai (JP / EN)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(
        song="ชื่อเพลง, ID, หรือเลือกจากรายการ",
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
        en_map = self._build_en_map(all_data)

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
            self._show_chart(interaction, matched_song, c, presence_str, en_map)
        else:
            self._show_song(interaction, matched_song, charts, presence_str, en_map)

    def _show_song(self, interaction: discord.Interaction, song: dict, charts: list[dict], server: str, en_map: dict):
        title = song.get("title", "(ไม่ทราบชื่อ)")
        en_name = en_map.get(song["id"])
        display = f"{title} ({en_name})" if en_name else title
        composer = song.get("composer", "(ไม่ทราบผู้แต่ง)")
        categories = song.get("categories", ["original"])
        category = categories[0] if categories else "original"

        embed = EmbedBuilder.hex("#FF66AA", f"🎵 {display}")
        embed.set_footer(text=f"ID: {song['id']} — Requested by {interaction.user.display_name}")
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

    def _show_chart(self, interaction: discord.Interaction, song: dict, chart: dict, server: str, en_map: dict):
        diff = chart["musicDifficulty"]
        title = song.get("title", "(ไม่ทราบชื่อ)")
        en_name = en_map.get(song["id"])
        display = f"{title} ({en_name})" if en_name else title
        level = chart.get("playLevel", "?")
        notes = chart.get("totalNoteCount", "?")
        color = DIFFICULTY_COLORS.get(diff, "#FFFFFF")
        label = DIFFICULTIES.get(diff, diff.upper())

        embed = EmbedBuilder.hex(color, f"🎵 {display} — {label} ★{level}")
        embed.set_footer(text=f"ID: {song['id']} — Requested by {interaction.user.display_name}")
        embed.add_inline_field("เซิร์ฟเวอร์", server, inline=False)
        embed.add_inline_field("โน้ตทั้งหมด", str(notes))

        interaction.followup.send(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="songs", description="แสดงรายชื่อเพลงทั้งหมดใน Project Sekai พร้อม ID")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(page="หมายเลขหน้า (เริ่มที่ 1)")
    async def songs(self, interaction: discord.Interaction, page: int = 1):
        await interaction.response.defer(ephemeral=True, thinking=True)

        all_data = await self._fetch_all()
        en_map = self._build_en_map(all_data)
        jp_pair = all_data.get("🇯🇵 JP")
        if jp_pair is None:
            await interaction.followup.send("ไม่สามารถโหลดข้อมูลเพลงได้", ephemeral=True)
            return

        musics, _ = jp_pair
        total = len(musics)
        total_pages = (total + SONGS_PER_PAGE - 1) // SONGS_PER_PAGE
        page = max(1, min(page, total_pages))
        start = (page - 1) * SONGS_PER_PAGE
        end = start + SONGS_PER_PAGE
        chunk = musics[start:end]

        lines = []
        for s in chunk:
            sid = s["id"]
            title = s.get("title", "?")
            en_name = en_map.get(sid)
            display = f"{title} ({en_name})" if en_name else title
            lines.append(f"`{sid:>4}` {display}")

        embed = EmbedBuilder.hex("#FF66AA", "🎵 รายชื่อเพลงทั้งหมด")
        embed.set_footer(text=f"หน้า {page}/{total_pages} — เพลง {total} เพลง")
        embed.description = "\n".join(lines)

        view = SongPaginationView(self, page, total_pages)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class SongPaginationView(discord.ui.View):
    def __init__(self, cog: Chart, page: int, total: int):
        super().__init__(timeout=60)
        self.cog = cog
        self.page = page
        self.total = total

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page <= 1:
            return
        self.page -= 1
        await self._refresh(interaction)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page >= self.total:
            return
        self.page += 1
        await self._refresh(interaction)

    async def _refresh(self, interaction: discord.Interaction):
        all_data = await self.cog._fetch_all()
        en_map = self.cog._build_en_map(all_data)
        jp_pair = all_data.get("🇯🇵 JP")
        if jp_pair is None:
            return
        musics, _ = jp_pair
        start = (self.page - 1) * SONGS_PER_PAGE
        end = start + SONGS_PER_PAGE
        chunk = musics[start:end]

        lines = []
        for s in chunk:
            sid = s["id"]
            title = s.get("title", "?")
            en_name = en_map.get(sid)
            display = f"{title} ({en_name})" if en_name else title
            lines.append(f"`{sid:>4}` {display}")

        embed = EmbedBuilder.hex("#FF66AA", "🎵 รายชื่อเพลงทั้งหมด")
        embed.set_footer(text=f"หน้า {self.page}/{self.total} — เพลง {len(musics)} เพลง")
        embed.description = "\n".join(lines)

        await interaction.response.edit_message(embed=embed, view=self)


async def setup(bot):
    await bot.add_cog(Chart(bot))
