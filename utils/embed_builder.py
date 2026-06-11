import discord
from datetime import datetime
from typing import Optional


class EmbedBuilder(discord.Embed):
    colors = {
        "primary": 0x5865F2,
        "success": 0x57F287,
        "warning": 0xFEE75C,
        "error": 0xED4245,
        "info": 0x00A8FC,
    }

    @classmethod
    def primary(cls, title: Optional[str] = None, description: Optional[str] = None):
        return cls(color=cls.colors["primary"], title=title, description=description)

    @classmethod
    def success(cls, title: Optional[str] = None, description: Optional[str] = None):
        return cls(color=cls.colors["success"], title=title, description=description)

    @classmethod
    def warning(cls, title: Optional[str] = None, description: Optional[str] = None):
        return cls(color=cls.colors["warning"], title=title, description=description)

    @classmethod
    def error(cls, title: Optional[str] = None, description: Optional[str] = None):
        return cls(color=cls.colors["error"], title=title, description=description)

    @classmethod
    def info(cls, title: Optional[str] = None, description: Optional[str] = None):
        return cls(color=cls.colors["info"], title=title, description=description)

    @classmethod
    def hex(cls, hex_color: str, title: Optional[str] = None, description: Optional[str] = None):
        hex_color = hex_color.lstrip("#")
        return cls(color=int(hex_color, 16), title=title, description=description)

    def set_primary(self, title: Optional[str] = None, description: Optional[str] = None):
        self.color = self.colors["primary"]
        if title:
            self.title = title
        if description:
            self.description = description
        return self

    def set_success(self, title: Optional[str] = None, description: Optional[str] = None):
        self.color = self.colors["success"]
        if title:
            self.title = title
        if description:
            self.description = description
        return self

    def set_warning(self, title: Optional[str] = None, description: Optional[str] = None):
        self.color = self.colors["warning"]
        if title:
            self.title = title
        if description:
            self.description = description
        return self

    def set_error(self, title: Optional[str] = None, description: Optional[str] = None):
        self.color = self.colors["error"]
        if title:
            self.title = title
        if description:
            self.description = description
        return self

    def set_info(self, title: Optional[str] = None, description: Optional[str] = None):
        self.color = self.colors["info"]
        if title:
            self.title = title
        if description:
            self.description = description
        return self

    def set_color_hex(self, hex_color: str, title: Optional[str] = None, description: Optional[str] = None):
        hex_color = hex_color.lstrip("#")
        self.color = int(hex_color, 16)
        if title:
            self.title = title
        if description:
            self.description = description
        return self

    def set_author(self, name: str, url: Optional[str] = None, icon_url: Optional[str] = None):
        super().set_author(name=name, url=url, icon_url=icon_url)
        return self

    def set_body(self, title: str, description: str, url: Optional[str] = None):
        self.title = title
        self.description = description
        if url:
            self.url = url
        return self

    def set_image_url(self, url: str):
        self.set_image(url=url)
        return self

    def set_thumbnail_url(self, url: str):
        self.set_thumbnail(url=url)
        return self

    def set_footer(self, text: str, icon_url: Optional[str] = None, timestamp=None):
        super().set_footer(text=text, icon_url=icon_url)
        if timestamp:
            self.timestamp = timestamp if isinstance(timestamp, datetime) else discord.utils.utcnow()
        return self

    def add_inline_field(self, name: str, value: str, inline: bool = True):
        self.add_field(name=name, value=value, inline=inline)
        return self

    def add_blank_field(self, inline: bool = False):
        self.add_field(name="\u200B", value="\u200B", inline=inline)
        return self
