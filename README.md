# SekaiUtils Discord Bot

Discord bot สำหรับเกม Project Sekai พร้อมระบบเสียง TTS, ข้อมูลเกม, และยืนยันตัวตน OAuth2

## คำสั่ง

### ข้อมูล Project Sekai

| คำสั่ง | รายละเอียด |
|---|---|
| `/help` | แสดงข้อมูลบอทและคำสั่ง |
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
├── fumi/authorizer.py        # /auth — ยืนยันตัวตน OAuth2
├── general/help.py           # /help — ข้อมูลบอท
├── voice/voice.py            # คำสั่งเสียง TTS
└── pjsk_info_summarize/      # ข้อมูลเกมเซไก
    ├── crystal_info/
    ├── otp/
    ├── team/
    └── time/
utils/
├── embed_builder.py          # Fluent API สำหรับสร้าง Embed
├── guild_config.py           # จัดการ config แยกตาม guild
└── admin_guard.py            # ระบบ allowlist สำหรับ admin
```

## ตัวแปรสภาพแวดล้อม (.env)

| ตัวแปร | คำอธิบาย |
|---|---|
| `BOT_TOKEN` | Token ของ Discord bot |
| `BOT_CREATOR` | Discord user ID ของผู้สร้างบอท |
| `DISCORD_CMD_AUTH_SK` | Secret key สำหรับคำสั่ง `/auth` |
| `DISCORD_BOT_OA2_LINK` | ลิงก์ OAuth2 สำหรับยืนยันตัวตน |
