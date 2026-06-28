import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_builder import EmbedBuilder

PRIMARY = "#5865F2"


class HelpSelect(discord.ui.Select):
    def __init__(self, bot, embeds: dict[str, discord.Embed]):
        options = [
            discord.SelectOption(label="ภาพรวม", description="คำสั่งทั้งหมดของบอท", emoji="🏠", value="__overview__"),
        ]
        for cog_name in sorted(embeds.keys()):
            if cog_name == "__overview__":
                continue
            options.append(discord.SelectOption(label=cog_name, value=cog_name))
        super().__init__(placeholder="เลือกหมวดหมู่คำสั่ง...", min_values=1, max_values=1, options=options)
        self.embeds = embeds

    async def callback(self, interaction: discord.Interaction):
        embed = self.embeds.get(self.values[0])
        if embed:
            await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, bot, embeds: dict[str, discord.Embed]):
        super().__init__(timeout=120)
        self.add_item(HelpSelect(bot, embeds))

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True


class Help(commands.Cog):
    __cog_name__ = "ทั่วไป"

    def __init__(self, bot):
        self.bot = bot

    def _build_embeds(self) -> dict[str, discord.Embed]:
        guilds = len(self.bot.guilds)
        users = sum(g.member_count or 0 for g in self.bot.guilds)
        cmds = self.bot.tree.get_commands()

        overview = EmbedBuilder.hex(PRIMARY, "✨ วิธีใช้บอท", "บอทเซไกที่รวบรวมข้อมูลและคำแนะนำสำหรับเกม Project Sekai")
        overview.set_thumbnail(url=self.bot.user.display_avatar.url)
        overview.add_inline_field("🤖 ชื่อ", self.bot.user.name)
        overview.add_inline_field("🆔 ID", str(self.bot.user.id))
        overview.add_inline_field("🖥 เซิร์ฟเวอร์", str(guilds))
        overview.add_inline_field("👥 ผู้ใช้", str(users))
        overview.add_inline_field("📜 คำสั่งทั้งหมด", str(len(cmds)))

        categories = []
        for cmd in cmds:
            cog = cmd.binding
            if cog:
                name = getattr(cog, "__cog_name__", None) or cog.__class__.__name__
            else:
                name = "อื่นๆ"
            if name not in categories:
                categories.append(name)
                overview.add_inline_field(f"📂 {name}", "\n".join(
                    f"`/{c.name}`" for c in cmds
                    if (getattr(c.binding, "__cog_name__", None) or (c.binding.__class__.__name__ if c.binding else "อื่นๆ")) == name
                ))

        overview.set_footer(text="ใช้เมนูด้านล่างเพื่อดูคำสั่งแยกตามหมวดหมู่")

        embeds: dict[str, discord.Embed] = {"__overview__": overview}

        for cmd in cmds:
            cog = cmd.binding
            if cog:
                cog_name = getattr(cog, "__cog_name__", None) or cog.__class__.__name__
            else:
                cog_name = "อื่นๆ"
            if cog_name not in embeds:
                cat_embed = EmbedBuilder.hex(PRIMARY, f"📂 {cog_name}")
                cat_embed.set_footer(text="ใช้เมนูด้านล่างเพื่อเปลี่ยนหมวดหมู่")
                embeds[cog_name] = cat_embed
            description = cmd.description or "ไม่มีคำอธิบาย"
            embeds[cog_name].add_inline_field(f"/{cmd.name}", description, inline=False)

        return embeds

    @discord.app_commands.command(name="help", description="แสดงข้อมูลบอทและคำสั่งทั้งหมด")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def help(self, interaction: discord.Interaction):
        embeds = self._build_embeds()
        view = HelpView(self.bot, embeds)
        await interaction.response.send_message(embed=embeds["__overview__"], view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
