# sekaiutils-discord

บอท Discord สำหรับข้อมูล Project Sekai (ภาษาไทย) พร้อมระบบเสียง TTS

## คำสั่ง

| คำสั่ง | รายละเอียด |
|---|---|
| `/help` | แสดงข้อมูลบอทและคำสั่งทั้งหมด |
| `/ข้อมูลการหาเพชร` | วิธีการฟาร์มเพชร |
| `/ข้อมูลเวลาเซิร์ฟ` | เวลาเซิร์ฟเวอร์ JP/Global |
| `/ข้อมูลการจัดทีม` | การจัดทีม |
| `/ข้อมูลการยืมไอดี` | การยืมไอดีและ OTP |
| `/join` | เชื่อมต่อห้องเสียง |
| `/leave` | ออกจากห้องเสียง |
| `/say <ข้อความ>` | พูดข้อความด้วย TTS (edge-tts) |
| `/voices` | รายชื่อเสียง TTS ที่ใช้ได้ |

## Run with Docker

```bash
# ใช้ image จาก GHCR
docker run -d --name sekaiutils \
  -e BOT_TOKEN=your_token \
  -e BOT_CREATOR=your_discord_id \
  ghcr.io/cltq/sekaiutils-discord:latest

# หรือใช้ docker compose
cp .env.example .env
# แก้ไข BOT_TOKEN ใน .env
docker compose up -d
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 bot.py
```
