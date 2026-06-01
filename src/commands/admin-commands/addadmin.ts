import { Discord, Slash, SlashOption } from "discordx";
import { SlashCommandUserOption, type CommandInteraction, type User } from "discord.js";
import { requireAdmin, addToAllowlist } from "../../helper/adminGuard.js";

@Discord()
export class AddAdmin {
  @Slash({ name: "addadmin", description: "Add a user to the admin allowlist" })
  async addAdmin(
    @SlashOption(
      new SlashCommandUserOption()
        .setName("user")
        .setDescription("The user to add as admin")
        .setRequired(true),
    )
    user: User,
    interaction: CommandInteraction,
  ): Promise<void> {
    if (!requireAdmin(interaction)) return;

    if (!interaction.guildId) {
      await interaction.reply({ content: "This command can only be used in a server.", ephemeral: true });
      return;
    }

    const added = addToAllowlist(interaction.guildId, user.id, user.username);
    if (!added) {
      await interaction.reply({ content: "That user is already in the allowlist.", ephemeral: true });
      return;
    }

    await interaction.reply({ content: `Added **${user.tag}** to the admin allowlist.`, ephemeral: true });
  }
}
