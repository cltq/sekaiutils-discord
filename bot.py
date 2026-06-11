import pathlib
import logging
import sys
import discord
from discord.ext import commands
import os

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logging.getLogger("discord").setLevel(logging.INFO)
logging.getLogger("discord.http").setLevel(logging.WARNING)

log = logging.getLogger("bot")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info("Bot is ready — starting sync")
    await bot.tree.sync()
    guilds = len(bot.guilds)
    users = sum(g.member_count or 0 for g in bot.guilds)
    cmds = bot.tree.get_commands()
    log.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    log.info("Connected to %d guilds", guilds)
    for g in bot.guilds:
        log.info("  Guild: %s (ID: %s) — %d members", g.name, g.id, g.member_count or 0)
    log.info("Total users visible: %d", users)
    log.info("Registered %d commands:", len(cmds))
    for c in cmds:
        log.info("  /%s — %s", c.name, c.description)
    log.info("Bot fully ready")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.custom,
            name="Custom Status",
            state="meow! :D - Fumi",
        )
    )


async def load_cogs():
    cogs_dir = pathlib.Path("cogs")
    paths = sorted(cogs_dir.rglob("*.py"))
    log.info("Found %d potential cog files", len(paths))
    for path in paths:
        if path.name == "__init__.py":
            continue
        module = ".".join(path.with_suffix("").parts)
        log.debug("Attempting to load %s from %s", module, path)
        try:
            await bot.load_extension(module)
            log.info("Loaded cog: %s", module)
        except Exception as e:
            log.error("Failed to load cog %s: %s", module, e)


async def main():
    log.info("Starting bot...")
    async with bot:
        log.info("Bot logged in, loading cogs...")
        await load_cogs()
        token = os.environ["BOT_TOKEN"]
        log.info("Connecting to gateway...")
        _original_identify = discord.gateway.DiscordWebSocket.identify

        async def _mobile_identify(self):
            payload = {
                "op": self.IDENTIFY,
                "d": {
                    "token": self.token,
                    "properties": {
                        "os": sys.platform,
                        "browser": "Discord iOS",
                        "device": "discord.py",
                    },
                    "compress": True,
                    "large_threshold": 250,
                },
            }
            if self.shard_id is not None and self.shard_count is not None:
                payload["d"]["shard"] = [self.shard_id, self.shard_count]
            state = self._connection
            if state._activity is not None or state._status is not None:
                payload["d"]["presence"] = {
                    "status": state._status,
                    "game": state._activity,
                    "since": 0,
                    "afk": False,
                }
            if state._intents is not None:
                payload["d"]["intents"] = state._intents.value
            await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
            await self.send_as_json(payload)

        discord.gateway.DiscordWebSocket.identify = _mobile_identify
        await bot.start(token)


if __name__ == "__main__":
    import asyncio
    log.info("Bot process started")
    asyncio.run(main())
