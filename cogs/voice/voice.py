import discord
from discord.ext import commands
from discord import app_commands
import edge_tts
from edge_tts.exceptions import NoAudioReceived
import tempfile
import os
import logging
import asyncio
from utils.guild_config import get_guild, set_guild

log = logging.getLogger(__name__)

DEFAULT_VOICE = "th-TH-NiwatNeural"
TTS_RETRIES = 3


def get_voice(interaction: discord.Interaction) -> str:
    cfg = get_guild(interaction.guild_id)
    return cfg.get("default_voice", DEFAULT_VOICE)


class Voice(commands.Cog):
    __cog_name__ = "เสียง"
    __cog_description__ = "คำสั่งเกี่ยวกับเสียงและ TTS"

    def __init__(self, bot):
        self.bot = bot
        self._read_locks: dict[int, asyncio.Lock] = {}

    async def ensure_voice(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                "คุณต้องอยู่ในห้องเสียงก่อนใช้คำสั่งนี้", ephemeral=True
            )
            return False
        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if vc:
            if vc.channel != channel:
                await vc.move_to(channel)
        else:
            await channel.connect()
        return True

    @discord.app_commands.command(name="join", description="เชื่อมต่อห้องเสียง")
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    @app_commands.describe(
        channel="ห้องเสียงที่จะเชื่อมต่อ (ไม่ใส่ = ห้องที่คุณอยู่)",
        auto_read="อ่านข้อความในแชทนี้ด้วย TTS อัตโนมัติ",
    )
    async def join(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel | None = None,
        auto_read: bool = True,
    ):
        target = channel or interaction.user.voice.channel if interaction.user.voice else None
        if not target:
            await interaction.response.send_message(
                "คุณต้องอยู่ในห้องเสียง หรือระบุห้องเสียง", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        vc = interaction.guild.voice_client
        if vc:
            if vc.channel != target:
                await vc.move_to(target)
                msg = f"ย้ายไป {target.mention} แล้ว"
            else:
                msg = f"อยู่ใน {target.mention} อยู่แล้ว"
        else:
            await target.connect()
            msg = f"เชื่อมต่อ {target.mention} แล้ว"

        if auto_read:
            set_guild(interaction.guild_id, "auto_read_channel_id", target.id)
            set_guild(interaction.guild_id, "auto_read_enabled", True)
            msg += " และเปิดอ่านข้อความอัตโนมัติ"
        else:
            set_guild(interaction.guild_id, "auto_read_enabled", False)
            msg += " และปิดอ่านข้อความอัตโนมัติ"

        await interaction.followup.send(msg, ephemeral=True)

    @discord.app_commands.command(name="leave", description="ตัดการเชื่อมต่อจากห้องเสียง")
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def leave(self, interaction: discord.Interaction):
        """Disconnect the bot from voice in this guild and disable auto-read."""
        await interaction.response.defer(ephemeral=True, thinking=True)

        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.followup.send("บอทไม่ได้เชื่อมต่อกับห้องเสียง", ephemeral=True)
            return

        try:
            await vc.disconnect()
            set_guild(interaction.guild_id, "auto_read_enabled", False)
            set_guild(interaction.guild_id, "auto_read_channel_id", None)
            await interaction.followup.send(
                "ตัดการเชื่อมต่อจากห้องเสียงแล้ว และปิดอ่านข้อความอัตโนมัติ",
                ephemeral=True,
            )
        except Exception as e:
            log.error("ไม่สามารถตัดการเชื่อมต่อห้องเสียง: %s", e, exc_info=True)
            await interaction.followup.send(f"ไม่สามารถตัดการเชื่อมต่อได้: {e}", ephemeral=True)

    async def _read_queue(
        self,
        lock: asyncio.Lock,
        text: str,
        voice: str,
        guild: discord.Guild,
    ):
        async with lock:
            await self._play_tts(text, voice, guild)

    async def _play_tts(
        self,
        text: str,
        voice: str,
        guild: discord.Guild,
    ):
        vc = guild.voice_client
        if not vc or not vc.is_connected():
            return

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name

            last_exc = None
            for attempt in range(TTS_RETRIES):
                try:
                    communicate = edge_tts.Communicate(text, voice=voice)
                    await communicate.save(temp_path)
                    last_exc = None
                    break
                except NoAudioReceived as e:
                    last_exc = e
                    log.warning(
                        "TTS ไม่ได้รับเสียง (ครั้งที่ %d/%d): %s",
                        attempt + 1, TTS_RETRIES, e,
                    )
                    if attempt < TTS_RETRIES - 1:
                        await asyncio.sleep(2 ** attempt)

            if last_exc:
                raise last_exc

            while vc.is_playing():
                vc.stop()

            def cleanup(error):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

            audio_source = discord.FFmpegPCMAudio(temp_path)
            vc.play(audio_source, after=cleanup)
        except Exception as e:
            log.error("TTS ผิดพลาด: %s", e, exc_info=True)
            if temp_path:
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

    @discord.app_commands.command(name="say", description="พูดข้อความด้วย TTS")
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    @app_commands.describe(
        text="ข้อความที่จะให้บอทพูด",
        voice="เสียงที่จะใช้ (ดูรายชื่อได้ที่ /voices)",
    )
    async def say(
        self,
        interaction: discord.Interaction,
        text: str,
        voice: str | None = None,
    ):
        if not await self.ensure_voice(interaction):
            return

        voice = voice or get_voice(interaction)
        await interaction.response.defer(ephemeral=True, thinking=True)

        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.followup.send(
                "บอทตัดการเชื่อมต่อจากห้องเสียง", ephemeral=True
            )
            return

        await self._play_tts(text, voice, interaction.guild)
        await interaction.followup.send(f"กำลังพูด: {text}", ephemeral=True)

    @discord.app_commands.command(name="voices", description="แสดงรายชื่อเสียง TTS ที่ใช้งานได้")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def voices(self, interaction: discord.Interaction):
        try:
            voices = await edge_tts.list_voices()
            lines = []
            for v in voices:
                lines.append(f"`{v['Name']}` — {v['Locale']} ({v['Gender']})")
            text = "\n".join(lines)
            if len(text) > 2000:
                text = text[:1997] + "..."
            await interaction.response.send_message(
                f"**รายชื่อเสียงที่มีให้ใช้ ({len(voices)} เสียง):**\n{text}",
                ephemeral=True,
            )
        except Exception as e:
            log.error("รายการเสียงผิดพลาด: %s", e, exc_info=True)
            await interaction.response.send_message(
                f"เกิดข้อผิดพลาด: {e}", ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return

        cfg = get_guild(message.guild.id)
        if not cfg.get("auto_read_enabled"):
            return

        vc = message.guild.voice_client
        if not vc or not vc.is_connected():
            return

        voice_channel_id = cfg.get("auto_read_channel_id")
        if not voice_channel_id:
            return
        voice_channel = message.guild.get_channel(voice_channel_id)
        if not isinstance(voice_channel, discord.VoiceChannel):
            return

        text_channel = discord.utils.get(
            message.guild.text_channels, name=voice_channel.name
        )
        if not text_channel or message.channel.id != text_channel.id:
            return

        voice = cfg.get("default_voice", DEFAULT_VOICE)
        lock = self._read_locks.setdefault(message.guild.id, asyncio.Lock())
        asyncio.create_task(self._read_queue(lock, message.content, voice, message.guild))

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if member != self.bot.user:
            return
        if before.channel and not after.channel:
            log.warning("ตัดการเชื่อมต่อ — กำลังเชื่อมต่อใหม่ทันที")
            cfg = get_guild(member.guild.id)
            channel_id = cfg.get("auto_read_channel_id") or before.channel.id
            for attempt in range(30):
                vc = member.guild.voice_client
                if vc and vc.is_connected():
                    return
                channel = member.guild.get_channel(channel_id)
                if isinstance(channel, discord.VoiceChannel):
                    try:
                        await channel.connect()
                        log.info("เชื่อมต่อใหม่สำเร็จ (ครั้งที่ %d)", attempt + 1)
                        return
                    except Exception:
                        pass
                await asyncio.sleep(2 ** min(attempt, 4))
            log.error("เชื่อมต่อใหม่ล้มเหลวหลังจาก 30 ครั้ง")


async def setup(bot):
    await bot.add_cog(Voice(bot))
