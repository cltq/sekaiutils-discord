import discord
from discord.ext import commands
from utils.embed_builder import EmbedBuilder


class TestEmbed(commands.Cog):
    @discord.app_commands.command(name="testembed", description="Test the embed builder")
    async def test_embed(self, interaction: discord.Interaction):
        embed = (
            EmbedBuilder()
            .set_primary("Primary Embed", "This is a primary embed")
            .add_blank_field()
            .add_inline_field("Inline Field", "This is an inline field")
            .add_inline_field("Another Inline Field", "This is another inline field")
            .set_author("Author Name", "https://example.com", "https://example.com/icon.png")
            .set_body("Body Title", "Body description text")
            .set_image_url("https://example.com/image.png")
            .set_thumbnail_url("https://example.com/thumb.png")
            .set_footer("Footer text", "https://example.com/footer-icon.png", True)
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(TestEmbed())
