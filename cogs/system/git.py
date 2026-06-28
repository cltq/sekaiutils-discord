import subprocess

import discord
from discord import app_commands
from discord.ext import commands

from utils.embed_builder import EmbedBuilder

REMOTE_CHOICES = [
    app_commands.Choice(name="GitHub", value="origin"),
    app_commands.Choice(name="Gitea (git.applefumi.xyz)", value="gitea"),
]

REMOTE_LABELS = {
    "origin": "GitHub",
    "gitea": "Gitea (git.applefumi.xyz)",
}


def _git_log(remote: str, all_commits: bool) -> str:
    try:
        subprocess.run(
            ["git", "fetch", "--quiet", remote, "main"],
            capture_output=True, timeout=15,
        )
        args = ["git", "log", f"{remote}/main", "--oneline", "--no-merges"]
        if not all_commits:
            args.extend(["-5"])
        result = subprocess.run(args, capture_output=True, text=True, timeout=15)
        lines = result.stdout.strip().splitlines()
        if not lines:
            return "(no commits found)"
        formatted = "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))
        return formatted
    except subprocess.CalledProcessError:
        return "(failed to fetch log)"
    except FileNotFoundError:
        return "(git not found)"
    except Exception as e:
        return f"({e})"


def _remote_info(remote: str) -> tuple[str, str] | None:
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", remote],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if not url:
            return None
        raw = url.replace(".git", "")
        if raw.startswith("https://"):
            parts = raw.split("/")
        elif ":" in raw and "@" in raw:
            parts = raw.split(":")[-1].split("/")
        else:
            return None
        if len(parts) >= 2:
            repo_path = f"{parts[-2]}/{parts[-1]}"
            host = parts[2] if raw.startswith("https://") else raw.split("@")[-1].split(":")[0]
            return (repo_path, host)
        return None
    except Exception:
        return None


class Git(commands.Cog):
    __cog_name__ = "Git"

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="git", description="ดู commits จาก remote (GitHub / Gitea)"
    )
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(
        remote="เลือก remote ที่ต้องการดู commits",
        all="แสดงทั้งหมด (true) หรือแค่ 5 ล่าสุด (false, default)",
        ephemeral="ตอบกลับแบบส่วนตัว (default: false)",
    )
    @app_commands.choices(remote=REMOTE_CHOICES)
    async def git(
        self,
        interaction: discord.Interaction,
        remote: str,
        all: bool = False,
        ephemeral: bool = False,
    ):
        await interaction.response.defer(ephemeral=ephemeral, thinking=True)

        embed = EmbedBuilder.hex("#F05032", "📋 Git Log")
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        log = _git_log(remote, all)
        label = REMOTE_LABELS.get(remote, remote)
        info = _remote_info(remote)
        if info:
            repo_path, host = info
            scheme = "https://"
            url = f"{scheme}{host}/{repo_path}"
            field_value = f"[`{repo_path}`]({url})\n```{log}```"
        else:
            repo_path = "?"
            field_value = f"```{log}```"
        embed.add_inline_field(
            f"🔗 {label} (using {remote}/main) - {remote}/{repo_path}",
            field_value,
            inline=False,
        )

        await interaction.followup.send(embed=embed, ephemeral=ephemeral)


async def setup(bot):
    await bot.add_cog(Git(bot))
