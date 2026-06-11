import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_builder import EmbedBuilder

PRIMARY = "#5865F2"


class Help(commands.Cog):
    __cog_name__ = "ทั่วไป"

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="help", description="แสดงข้อมูลบอทและคำสั่งทั้งหมด")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def help(self, interaction: discord.Interaction):
        cmds = self.bot.tree.get_commands()
        guilds = len(self.bot.guilds)
        users = sum(g.member_count or 0 for g in self.bot.guilds)

        embed = EmbedBuilder.hex(PRIMARY, "ข้อมูลบอท", f"บอทเซไกที่รวบรวมข้อมูลและคำแนะนำสำหรับเกม Project Sekai")
        embed.add_inline_field("ชื่อ", self.bot.user.name)
        embed.add_inline_field("ID", self.bot.user.id)
        embed.add_inline_field("เซิร์ฟเวอร์", str(guilds))
        embed.add_inline_field("ผู้ใช้ทั้งหมด", str(users))
        embed.add_inline_field("คำสั่งทั้งหมด", str(len(cmds)))

        for cog_name, cog in self.bot.cogs.items():
            cog_cmds = cog.get_app_commands()
            if not cog_cmds:
                continue
            names = "\n".join(f"/{c.name}" for c in cog_cmds)
            embed.add_inline_field(f"__{cog_name}__", names, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
