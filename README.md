# sekaiutils-discord

บอท Discord สำหรับข้อมูล Project Sekai (ภาษาไทย) พร้อมระบบเสียง TTS

## คำสั่ง

### ข้อมูล

| คำสั่ง | รายละเอียด |
|---|---|
| `/help` | แสดงข้อมูลบอทและคำสั่ง |
| `/ข้อมูลการหาเพชร` | วิธีการฟาร์มเพชร |
| `/ข้อมูลเวลาเซิร์ฟ` | เวลาเซิร์ฟเวอร์ JP/Global |
| `/ข้อมูลการจัดทีม` | การจัดทีม |
| `/ข้อมูลการยืมไอดี` | การยืมไอดีและ OTP |

### เสียง

| คำสั่ง | รายละเอียด |
|---|---|
| `/join [channel] [auto_read]` | เชื่อมต่อห้องเสียง (default: auto_read=True) |
| `/leave` | ออกจากห้องเสียง |
| `/say <ข้อความ> [voice]` | พูดข้อความด้วย TTS |
| `/voices` | รายชื่อเสียง TTS ที่ใช้ได้ |
| `/control [mute] [deafen]` | ปิดไมค์/ปิดหูบอท (default: deafen) |

## การติดตั้ง

```bash
# อัตโนมัติ — ติดตั้งทุกอย่างแล้วรันเลย
./auto.sh

# หรือทำทีละขั้น
cp .env.example .env
# แก้ไข BOT_TOKEN ใน .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 bot.py
```

### Docker

```bash
cp .env.example .env
# แก้ไข BOT_TOKEN ใน .env
docker compose up -d
```

## ระบบ Auto-Read

เชื่อมต่อห้องเสียงและให้บอทอ่านข้อความในแชทอัตโนมัติ:

```
/join                   # เชื่อมต่อห้องที่คุณอยู่ + เปิด auto-read
/join auto_read:False   # เชื่อมต่ออย่างเดียว ไม่ต้องอ่าน
/join channel:#general  # เลือกห้องเสียง + เปิด auto-read
```

บอทจะ TTS ข้อความทุกข้อความในแชทที่ใช้คำสั่ง `/join`
