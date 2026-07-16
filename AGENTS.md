# AGENTS.md — สำหรับ AI Agents

## โครงสร้างโปรเจกต์

```
cogs/                          # โหลดทั้งหมดอัตโนมัติ (ยกเว้น __init__.py)
├── fumi/authorizer.py         # /auth — OAuth2 verification
├── general/
│   ├── help.py                # /help — Bot info
│   └── info.py                # /info — Bot info embed
├── system/
│   ├── git.py                 # /git — Git log viewer
│   ├── changelog.py           # /changelog — Changelog viewer (reads from changelogs/)
│   └── uptime.py              # /uptime — Bot uptime + latency
├── voice/voice.py             # TTS voice commands (edge-tts)
├── prosekai/chart/chart.py    # /chart, /songs — chart viewer + song list
└── pjsk_info_summarize/       # Static info commands
    ├── crystal_info/crystal_info.py   # /ข้อมูลการหาเพชร
    ├── otp/onetime_password.py        # /ข้อมูลการยืมไอดี
    ├── team/team.py                   # /ข้อมูลการจัดทีม
    └── time/time.py                   # /ข้อมูลเวลาเซิร์ฟ
utils/
├── embed_builder.py           # EmbedBuilder subclass (fluent API)
├── guild_config.py            # JSON-based per-guild config
└── admin_guard.py             # Admin allowlist + BOT_CREATOR check
changelogs/                    # Changelog markdown files (changelog-YYYY-MM-DD-HH-MM.md)
unused/                        # ไม่โหลด, พร้อม reactivate
```

## กฎและแนวทาง

### Cog conventions
- แต่ละ cog ต้องมี `async def setup(bot): await bot.add_cog(CogName(bot))`
- ใช้ `@discord.app_commands.command()` สำหรับ slash commands
- ใช้ `@app_commands.allowed_contexts()` และ `@app_commands.allowed_installs()` ตามความเหมาะสม
- ใช้ `@app_commands.describe()` สำหรับอธิบายพารามิเตอร์
- ใช้ `ephemeral=True` สำหรับการตอบกลับส่วนตัว

### EmbedBuilder
```python
from utils.embed_builder import EmbedBuilder

EmbedBuilder.success("Title", "Description")     # สีเขียว
EmbedBuilder.error("Title", "Description")       # สีแดง
EmbedBuilder.warning("Title", "Description")     # สีเหลือง
EmbedBuilder.info("Title", "Description")        # สีฟ้า
EmbedBuilder.primary("Title", "Description")     # สีน้ำเงิน
EmbedBuilder.hex("#FF00FF", "Title", "Text")     # สีกำหนดเอง
EmbedBuilder("Title").set_color_hex("#AABBCC").add_inline_field("k", "v")
```

### Guild config
```python
from utils.guild_config import get_guild, set_guild
cfg = get_guild(guild_id)       # คืนค่า dict
set_guild(guild_id, key, val)   # กำหนดค่า
```

### Admin guard
```python
from utils.admin_guard import admin_check, is_user_admin

@admin_check()                  # decorator สำหรับ slash command
async def cmd(self, i): ...
```

### ข้อควรรู้
- Bot ใช้ `discord.py` 2.5+, Python 3.13
- Voice/TTS ใช้ edge-tts (Microsoft Edge TTS) + ffmpeg
- Info commands โหลดข้อความจาก `.txt` files ใน directory ของตัวเอง
- `unused/` contains archived/admin commands ที่ไม่ถูกโหลดอัตโนมัติ
- `.env` ใช้ `python-dotenv` style (อ่านด้วย `set -a; source .env; set +a` ใน auto.sh)
- Docker image: `python:3.13-slim` + ffmpeg
- Changelogs เก็บใน `changelogs/` ชื่อไฟล์ `changelog-YYYY-MM-DD-HH-MM.md` (markdown, ไม่เขียนทับไฟล์เก่า)

### การเพิ่ม cog ใหม่
1. สร้าง `.py` file ใน `cogs/<category>/`
2. cog class รับ `self.bot` ใน `__init__`
3. ลงท้ายด้วย `async def setup(bot): await bot.add_cog(CogName(bot))`
4. bot จะโหลดอัตโนมัติ (rglob `.py` ข้าม `__init__.py`)
