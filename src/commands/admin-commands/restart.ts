import { Discord, Slash } from "discordx";
import type { CommandInteraction } from "discord.js";
import { requireAdmin } from "../../helper/adminGuard.js";

@Discord()
export class Restart {
  @Slash({ name: "restart", description: "Restart the bot process" })
  async restart(interaction: CommandInteraction): Promise<void> {
    if (!requireAdmin(interaction)) return;

    await interaction.reply({ content: "Restarting...", ephemeral: true });
    process.exit(1);
  }
}
