import asyncio
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

_bot_connected = False
_restart_requested = False


def request_restart():
    global _restart_requested
    _restart_requested = True


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


@bot.event
async def on_connect():
    global _bot_connected
    _bot_connected = True
    log.info("Connected to Discord gateway")


@bot.event
async def on_disconnect():
    global _bot_connected
    _bot_connected = False
    log.warning("Disconnected from Discord gateway")


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


HEALTH_HOST = "0.0.0.0"
HEALTH_PORT = 8899


async def _health_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    await reader.readuntil(b"\r\n\r\n")
    status = b"ok" if _bot_connected else b"disconnected"
    http_status = 200 if _bot_connected else 503
    body = f"{http_status} {status.decode()}"
    response = (
        f"HTTP/1.1 {http_status} {status.decode().title()}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n\r\n"
        f"{body}"
    ).encode()
    writer.write(response)
    await writer.drain()
    writer.close()


async def run_health_server():
    server = await asyncio.start_server(_health_handler, HEALTH_HOST, HEALTH_PORT)
    log.info("Health check server listening on %s:%d", HEALTH_HOST, HEALTH_PORT)
    async with server:
        await server.serve_forever()


async def keep_alive():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.custom,
                    name="Custom Status",
                    state="meow! :D - Fumi",
                )
            )
        except Exception:
            pass
        await asyncio.sleep(60)


def _patch_mobile_identify():
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


async def run_bot_forever():
    token = os.environ["BOT_TOKEN"]
    _patch_mobile_identify()
    while True:
        try:
            log.info("Starting bot session...")
            async with bot:
                log.info("Loading cogs...")
                await load_cogs()
                log.info("Connecting to Discord gateway...")
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(bot.start(token))
                    tg.create_task(keep_alive())
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.error("Bot session ended with error: %s", e, exc_info=True)

        if _restart_requested:
            log.info("Restart requested — exiting process")
            sys.exit(0)

        log.warning("Reconnecting in 10 seconds...")
        await asyncio.sleep(10)


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(run_health_server())
        tg.create_task(run_bot_forever())


if __name__ == "__main__":
    log.info("Bot process started")
    asyncio.run(main())
