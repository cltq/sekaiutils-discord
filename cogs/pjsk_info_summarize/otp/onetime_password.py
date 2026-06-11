import pathlib
import discord
from discord.ext import commands
from utils.embed_builder import EmbedBuilder
from discord import app_commands

DATA_FILE = pathlib.Path(__file__).parent / "onetime_password.txt"

AQUA = "#00FFFF"


class OnetimePassword(commands.Cog):
    __cog_name__ = "สรุปการยืมไอดี"

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="ข้อมูลการยืมไอดี", description="แสดงข้อมูลสรุปการยืมไอดีและการใช้รหัสผ่านเข้าเกมแบบครั้งเดียวในเซไก")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def summary(self, interaction: discord.Interaction):
        text = DATA_FILE.read_text(encoding="utf-8")
        embed = EmbedBuilder().set_color_hex(AQUA, "สรุปการยืมไอดี", text)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(OnetimePassword(bot))
