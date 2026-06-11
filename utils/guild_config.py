import json

CONFIG_PATH = "guild_configs.json"

DEFAULT_CONFIG = {
    "default_voice": "th-TH-NiwatNeural",
    "auto_read_channel_id": None,
    "auto_read_enabled": False,
}


def load():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def get_guild(guild_id: int) -> dict:
    config = load()
    return config.get(str(guild_id), dict(DEFAULT_CONFIG))


def set_guild(guild_id: int, key: str, value):
    config = load()
    gid = str(guild_id)
    if gid not in config:
        config[gid] = dict(DEFAULT_CONFIG)
    config[gid][key] = value
    save(config)
