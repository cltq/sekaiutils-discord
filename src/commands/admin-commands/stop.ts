import { Discord, Slash } from "discordx";
import type { CommandInteraction } from "discord.js";
import { requireAdmin } from "../../helper/adminGuard.js";

@Discord()
export class Stop {
  @Slash({ name: "stop", description: "Stop the bot process" })
  async stop(interaction: CommandInteraction): Promise<void> {
    if (!requireAdmin(interaction)) return;

    await interaction.reply({ content: "Shutting down...", ephemeral: true });
    process.exit(0);
  }
}
