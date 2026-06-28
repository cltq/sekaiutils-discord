# SekaiUtils Discord Bot

Discord bot สำหรับเกม Project Sekai พร้อมระบบเสียง TTS, ข้อมูลเกม, ยืนยันตัวตน OAuth2, และคำสั่งระบบ

## Features

### ข้อมูล Project Sekai
| คำสั่ง | รายละเอียด |
|---|---|
| `/help` | แสดงข้อมูลบอทและคำสั่งทั้งหมด |
| `/info` | แสดงข้อมูลบอท (ชื่อ, ID, เจ้าของ, อัปไทม์, status page) |
| `/chart <song> [difficulty]` | ค้นหา chart เพลงพร้อมแสดงรูปภาพ |
| `/songs [page]` | แสดงรายชื่อเพลงทั้งหมดใน Project Sekai |
| `/ข้อมูลการหาเพชร` | วิธีการฟาร์มเพชรในเซไก |
| `/ข้อมูลการจัดทีม` | การจัดทีมและการทำคะแนน |
| `/ข้อมูลเวลาเซิร์ฟ` | เวลาเซิร์ฟเวอร์ JP/Global |
| `/ข้อมูลการยืมไอดี` | การยืมไอดีและรหัสผ่านแบบครั้งเดียว (OTP) |

### เสียง TTS
| คำสั่ง | รายละเอียด |
|---|---|
| `/join [channel] [auto_read]` | เชื่อมต่อห้องเสียง (default: auto_read=True) |
| `/leave` | ออกจากห้องเสียง |
| `/say <text> [voice]` | พูดข้อความด้วย TTS |
| `/voices` | แสดงรายชื่อเสียง TTS ที่ใช้งานได้ |

### ยืนยันตัวตน
| คำสั่ง | รายละเอียด |
|---|---|
| `/auth <secret_key>` | รับลิงก์ OAuth2 สำหรับเชื่อมต่อบอท (ตอบกลับแบบ ephemeral) |

### ระบบ
| คำสั่ง | รายละเอียด |
|---|---|
| `/git [remote] [all]` | ดู commits จาก remote (GitHub / Gitea) |

## Health Check

บอทเปิด HTTP server บนพอร์ต `88990` สำหรับ health check:
```bash
curl http://localhost:88990
# => ok
```

## การติดตั้ง

### ทั่วไป
```bash
cp .env.example .env
# แก้ไข .env: ใส่ BOT_TOKEN, DISCORD_CMD_AUTH_SK, DISCORD_BOT_OA2_LINK
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 bot.py
```

### อัตโนมัติ
```bash
./auto.sh
```

### Docker
```bash
cp .env.example .env
docker compose up -d
```

## ระบบ Auto-Read

เชื่อมต่อห้องเสียงและให้บอทอ่านข้อความในแชทอัตโนมัติด้วย TTS:

```
/join                     # เชื่อมต่อห้องที่คุณอยู่ + เปิด auto-read
/join auto_read:False     # เชื่อมต่ออย่างเดียว ไม่เปิด auto-read
/join channel:#general    # เลือกห้องเสียง + เปิด auto-read
```

บอทจะ TTS ข้อความทุกข้อความในแชทที่มีชื่อเดียวกับห้องเสียงที่เชื่อมต่อ

## โครงสร้างโปรเจกต์

```
cogs/
├── fumi/authorizer.py            # /auth — OAuth2 verification
├── general/
│   ├── help.py                   # /help — Bot info
│   └── info.py                   # /info — Bot details, uptime
├── prosekai/
│   ├── chart/chart.py            # /chart, /songs — Chart viewer + song list
│   └── info_summarize/           # Static info commands
│       ├── crystal_info/
│       ├── otp/
│       ├── team/
│       └── time/
├── system/git.py                 # /git — Git log viewer
└── voice/voice.py                # TTS voice commands (edge-tts)
utils/
├── embed_builder.py              # EmbedBuilder subclass (fluent API)
├── guild_config.py               # JSON-based per-guild config
└── admin_guard.py                # Admin allowlist + BOT_CREATOR check
unused/                           # Archived/admin commands (not loaded)
```

## ตัวแปรสภาพแวดล้อม (.env)

| ตัวแปร | คำอธิบาย |
|---|---|
| `BOT_TOKEN` | Token ของ Discord bot |
| `BOT_CREATOR` | Discord user ID ของผู้สร้างบอท |
| `DISCORD_CMD_AUTH_SK` | Secret key สำหรับคำสั่ง `/auth` |
| `DISCORD_BOT_OA2_LINK` | ลิงก์ OAuth2 สำหรับยืนยันตัวตน |

## Credits

พัฒนาโดย Fumi (cltq)
