#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
msg()  { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[-]${NC} $1"; }

detect_os() {
    case "$(uname -s)" in
        Linux*)   echo linux;;
        Darwin*)  echo macos;;
        MINGW*|MSYS*|CYGWIN*) echo windows;;
        *)        echo unknown;;
    esac
}

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif command -v lsb_release &>/dev/null; then
        lsb_release -si | tr '[:upper:]' '[:lower:]'
    else
        echo unknown
    fi
}

install_pkg() {
    local pkg=$1
    msg "ติดตั้ง $pkg..."
    case $DISTRO in
        ubuntu|debian|pop|linuxmint|elementary|kali)
            sudo apt-get update -qq && sudo apt-get install -y -qq "$pkg" ;;
        fedora|rhel|centos)
            sudo dnf install -y "$pkg" ;;
        arch|manjaro|endeavouros)
            sudo pacman -S --noconfirm "$pkg" ;;
        alpine)
            sudo apk add "$pkg" ;;
        opensuse*|suse)
            sudo zypper install -y "$pkg" ;;
        *) warn "ไม่รู้จัก distro '$DISTRO' — กรุณาติดตั้ง $pkg เอง" ;;
    esac
}

OS=$(detect_os)
DISTRO=$(detect_distro)
msg "ระบบ: $OS ($DISTRO)"

# ---- Python ----
PYTHON=
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON=$(command -v "$cmd")
        break
    fi
done

if [ -z "$PYTHON" ]; then
    warn "ไม่พบ Python กำลังติดตั้ง..."
    case $OS in
        linux) install_pkg python3 ;;
        macos)
            if command -v brew &>/dev/null; then brew install python
            else err "กรุณาติดตั้ง Python จาก https://python.org"; exit 1; fi ;;
        windows) err "กรุณาติดตั้ง Python จาก https://python.org"; exit 1 ;;
    esac
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then PYTHON=$(command -v "$cmd"); break; fi
    done
fi
msg "Python: $($PYTHON --version 2>&1)"

# ---- ffmpeg ----
if ! command -v ffmpeg &>/dev/null; then
    warn "ไม่พบ ffmpeg กำลังติดตั้ง..."
    case $OS in
        linux) install_pkg ffmpeg ;;
        macos)
            if command -v brew &>/dev/null; then brew install ffmpeg
            else warn "กรุณาติดตั้ง ffmpeg: brew install ffmpeg"; fi ;;
        windows) warn "กรุณาติดตั้ง ffmpeg จาก https://ffmpeg.org";;
    esac
fi
command -v ffmpeg &>/dev/null && msg "ffmpeg: $(ffmpeg -version 2>&1 | head -1)" || warn "ffmpeg ไม่พร้อม — เสียงจะไม่ทำงาน"

# ---- Git pull ----
msg "ตรวจสอบการอัปเดตจาก GitHub..."
REMOTE_URL="origin"
if command -v git &>/dev/null; then
    if git remote get-url "$REMOTE_URL" &>/dev/null; then
        git fetch "$REMOTE_URL" 2>&1 || warn "fetch ล้มเหลว — ข้าม"
        LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "")
        REMOTE=$(git rev-parse "@{upstream}" 2>/dev/null || echo "")
        if [ -n "$LOCAL" ] && [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
            msg "พบการอัปเดต — กำลัง pull..."
            git pull --ff-only "$REMOTE_URL" main 2>&1 || warn "pull ล้มเหลว — ใช้โค้ดเดิม"
        else
            msg "โค้ดล่าสุดแล้ว"
        fi
    else
        warn "ไม่มี remote '$REMOTE_URL' — ข้าม git pull"
    fi
else
    warn "ไม่พบ git — ข้ามการตรวจสอบอัปเดต"
fi

# ---- venv & deps ----
if [ "$OS" = windows ]; then
    msg "Windows: ไม่ใช้ virtual environment"
    "$PYTHON" -m pip install -q -r requirements.txt
    PIP="$PYTHON -m pip"
    RUNNER="$PYTHON"
else
    if [ ! -d .venv ]; then
        msg "สร้าง virtual environment..."
        "$PYTHON" -m venv .venv
    fi
    msg "ติดตั้ง dependencies..."
    .venv/bin/pip install -q -r requirements.txt
    PIP=".venv/bin/pip"
    RUNNER=".venv/bin/python3"
fi

# ---- .env ----
if [ ! -f .env ]; then
    err "ไม่พบไฟล์ .env"
    err "คัดลอกจาก .env.example และใส่ BOT_TOKEN"
    exit 1
fi

set -a; source .env; set +a
msg "เริ่มบอท..."
exec $RUNNER bot.py
