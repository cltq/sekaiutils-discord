import os
from discord.ext import commands
from discord import app_commands


ALLOWLIST_PATH = "allowlist.txt"


def _parse_allowlist():
    entries = []
    try:
        with open(ALLOWLIST_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                parts = line.split(":", 1)
                if len(parts) != 2:
                    continue
                guild_id = parts[0].strip()
                rest = parts[1].strip()
                user_parts = rest.split(",", 1)
                if len(user_parts) != 2:
                    continue
                user_id = user_parts[0].strip()
                entries.append((guild_id, user_id))
    except FileNotFoundError:
        pass
    return entries


def is_user_admin(user_id: str, guild_id: str) -> bool:
    if os.environ.get("BOT_CREATOR") == user_id:
        return True
    return (guild_id, user_id) in _parse_allowlist()


def add_to_allowlist(guild_id: str, user_id: str, username: str):
    entries = _parse_allowlist()
    if (guild_id, user_id) in entries:
        return False
    with open(ALLOWLIST_PATH, "a") as f:
        f.write(f"{guild_id}: {user_id}, {username}\n")
    return True


def admin_check():
    async def predicate(interaction: discord.Interaction):
        if not interaction.guild_id:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return False
        if not is_user_admin(str(interaction.user.id), str(interaction.guild_id)):
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return False
        return True
    return app_commands.check(predicate)
