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
        args = ["git", "log", f"{remote}/main", "--oneline"]
        if not all_commits:
            args.extend(["-5"])
        result = subprocess.run(args, capture_output=True, text=True, timeout=15)
        output = result.stdout.strip()
        return output or "(no commits found)"
    except subprocess.CalledProcessError:
        return "(failed to fetch log)"
    except FileNotFoundError:
        return "(git not found)"
    except Exception as e:
        return f"({e})"


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
        all="แสดงทุก commits (true) หรือแค่ 5 ล่าสุด (false)",
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
        embed.add_inline_field(
            f"🔗 {label} (using {remote}/main)", f"```{log}```", inline=False
        )

        await interaction.followup.send(embed=embed, ephemeral=ephemeral)


async def setup(bot):
    await bot.add_cog(Git(bot))
