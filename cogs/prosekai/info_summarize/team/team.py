import pathlib
import discord
from discord.ext import commands
from utils.embed_builder import EmbedBuilder
from discord import app_commands

DATA_FILE = pathlib.Path(__file__).parent / "team.txt"

AQUA = "#00FFFF"


class Team(commands.Cog):
    __cog_name__ = "สรุปการจัดทีม"

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="ข้อมูลการจัดทีม", description="แสดงข้อมูลสรุปการจัดทีมและคะแนนในเซไก")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def summary(self, interaction: discord.Interaction):
        text = DATA_FILE.read_text(encoding="utf-8")
        embed = EmbedBuilder().set_color_hex(AQUA, "สรุปการจัดทีม", text)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Team(bot))
