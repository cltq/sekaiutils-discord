import { EmbedBuilder } from "../helper/EmbedBuilder.js";
import type { CommandInteraction } from "discord.js";
import { Discord, Slash } from "discordx";

@Discord()
export class TestEmbed {
  @Slash({ name: "testembed", description: "Test the embed builder" })
  async testEmbed(interaction: CommandInteraction): Promise<void> {
    const embed = new EmbedBuilder()
      .setPrimary("Primary Embed", "This is a primary embed")
      .setAuthor("Author Name", "https://example.com", "https://example.com/icon.png")
      .setBody("Body Title", "Body description text")
      .addBlankField()
      .addInlineField("Inline Field", "This is an inline field")
      .addInlineField("Another Inline Field", "This is another inline field")
      .setImageUrl("https://example.com/image.png")
      .setThumbnailUrl("https://example.com/thumb.png")
      .setFooter("Footer text", "https://example.com/footer-icon.png", true)
      .addButton("Click me", "button_click_id")
      .addLinkButton("Visit Site", "https://example.com");

    await interaction.reply(embed.toMessageOptions());
  }
}
