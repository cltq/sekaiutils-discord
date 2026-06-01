import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import type { CommandInteraction } from "discord.js";

interface AllowlistEntry {
  guildId: string;
  userId: string;
  username: string;
}

const ALLOWLIST_PATH = resolve(process.cwd(), "allowlist.txt");

function parseAllowlist(): AllowlistEntry[] {
  if (!existsSync(ALLOWLIST_PATH)) return [];

  const content = readFileSync(ALLOWLIST_PATH, "utf-8");
  const entries: AllowlistEntry[] = [];

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("//")) continue;

    const match = trimmed.match(/^(\d+):\s*(\d+),\s*(.+)$/);
    if (match) {
      entries.push({
        guildId: match[1],
        userId: match[2],
        username: match[3].trim(),
      });
    }
  }

  return entries;
}

function saveAllowlist(entries: AllowlistEntry[]): void {
  const lines = entries.map(
    (e) => `${e.guildId}: ${e.userId}, ${e.username}`,
  );
  writeFileSync(
    ALLOWLIST_PATH,
    "// allowlist.txt\n// Format: guildId: userId, username\n// One entry per line\n\n" +
      lines.join("\n") +
      "\n",
    "utf-8",
  );
}

export function isUserAdmin(userId: string, guildId: string): boolean {
  if (process.env.BOT_CREATOR === userId) return true;
  const entries = parseAllowlist();
  return entries.some(
    (e) => e.guildId === guildId && e.userId === userId,
  );
}

export function requireAdmin(
  interaction: CommandInteraction,
): boolean {
  if (!interaction.guildId) return false;
  const allowed = isUserAdmin(interaction.user.id, interaction.guildId);
  if (!allowed) {
    void interaction.reply({
      content: "You do not have permission to use this command.",
      ephemeral: true,
    });
  }
  return allowed;
}

export function addToAllowlist(
  guildId: string,
  userId: string,
  username: string,
): boolean {
  const entries = parseAllowlist();
  if (entries.some((e) => e.guildId === guildId && e.userId === userId)) {
    return false;
  }
  entries.push({ guildId, userId, username });
  saveAllowlist(entries);
  return true;
}
