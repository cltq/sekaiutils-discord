import discord
from discord.ext import commands
from discord import app_commands
import edge_tts
import tempfile
import os
import logging
import asyncio

log = logging.getLogger(__name__)

DEFAULT_VOICE = "th-TH-PremadeeNeural"


class Voice(commands.Cog):
    __cog_name__ = "เสียง"
    __cog_description__ = "คำสั่งเกี่ยวกับเสียงและ TTS"

    def __init__(self, bot):
        self.bot = bot

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

    @discord.app_commands.command(name="join", description="เชื่อมต่อห้องเสียงของผู้ใช้")
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                "คุณต้องอยู่ในห้องเสียงก่อน", ephemeral=True
            )
            return
        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if vc:
            if vc.channel != channel:
                await vc.move_to(channel)
                await interaction.response.send_message(
                    f"ย้ายไป {channel.mention} แล้ว", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"อยู่ใน {channel.mention} อยู่แล้ว", ephemeral=True
                )
        else:
            await channel.connect()
            await interaction.response.send_message(
                f"เชื่อมต่อ {channel.mention} แล้ว", ephemeral=True
            )

    @discord.app_commands.command(name="leave", description="ออกจากห้องเสียง")
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect(force=True)
            await interaction.response.send_message(
                "ออกจากห้องเสียงแล้ว", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "บอทไม่ได้อยู่ในห้องเสียง", ephemeral=True
            )

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

        voice = voice or DEFAULT_VOICE
        await interaction.response.defer(ephemeral=True, thinking=True)

        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.followup.send(
                "บอทตัดการเชื่อมต่อจากห้องเสียง", ephemeral=True
            )
            return

        try:
            communicate = edge_tts.Communicate(text, voice=voice)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name

            await communicate.save(temp_path)

            while vc.is_playing():
                vc.stop()

            def cleanup(error):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

            audio_source = discord.FFmpegPCMAudio(temp_path)
            vc.play(audio_source, after=cleanup)
            await interaction.followup.send(f"กำลังพูด: {text}", ephemeral=True)

        except Exception as e:
            log.error("TTS error: %s", e, exc_info=True)
            await interaction.followup.send(
                f"เกิดข้อผิดพลาด: {e}", ephemeral=True
            )
            try:
                os.unlink(temp_path)
            except Exception:
                pass

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
            log.error("voices error: %s", e, exc_info=True)
            await interaction.response.send_message(
                f"เกิดข้อผิดพลาด: {e}", ephemeral=True
            )

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
            log.warning("Bot was disconnected from voice channel")
            vc = member.guild.voice_client
            if vc:
                await vc.disconnect(force=True)


async def setup(bot):
    await bot.add_cog(Voice(bot))
