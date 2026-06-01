import { Discord, Slash } from "discordx";
import type { CommandInteraction } from "discord.js";
import { requireAdmin } from "../../helper/adminGuard.js";
import { bot } from "../../main.js";

@Discord()
export class SyncSlash {
  @Slash({ name: "syncslash", description: "Re-synchronize all slash commands with Discord" })
  async syncSlash(interaction: CommandInteraction): Promise<void> {
    if (!requireAdmin(interaction)) return;

    await interaction.deferReply({ ephemeral: true });
    await bot.initApplicationCommands();
    await interaction.editReply({ content: "Slash commands have been re-synchronized." });
  }
}
