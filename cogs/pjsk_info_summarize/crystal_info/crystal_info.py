import pathlib
import discord
from discord.ext import commands
from utils.embed_builder import EmbedBuilder
from discord import app_commands

DATA_FILE = pathlib.Path(__file__).parent / "crystal_info.txt"

MINT = "#98FF98"


class Summary(commands.Cog):
    __cog_name__ = "สรุปการหาเพชร"

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="ข้อมูลการหาเพชร", description="แสดงข้อมูลสรุปการหาเพชรในเซไก")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def summary(self, interaction: discord.Interaction):
        text = DATA_FILE.read_text(encoding="utf-8")
        sections = self._parse_sections(text)

        embed = EmbedBuilder().set_color_hex(MINT, "สรุปการหาเพชร", "")
        for title, content in sections:
            embed.add_inline_field(title, content, inline=False)

        await interaction.response.send_message(embed=embed)

    def _parse_sections(self, text: str) -> list[tuple[str, str]]:
        lines = text.strip().splitlines()
        sections = []
        current_title = None
        current_lines = []
        state = 0

        for line in lines:
            if line.startswith("==="):
                if state == 0:
                    state = 1
                elif state == 1:
                    state = 2
                elif state == 2:
                    if current_title is not None:
                        sections.append((current_title, "\n".join(current_lines).strip()))
                        current_lines = []
                        current_title = None
                    state = 1
                continue

            stripped = line.strip()
            if not stripped:
                continue

            if state == 1:
                current_title = stripped
            elif state == 2:
                current_lines.append(line)

        if current_title is not None:
            sections.append((current_title, "\n".join(current_lines).strip()))

        return sections


async def setup(bot):
    await bot.add_cog(Summary(bot))
