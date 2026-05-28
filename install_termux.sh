#!/data/data/com.termux/files/usr/bin/bash
# Script otomatis setup Twitter Downloader Bot di Termux

set -e  # Stop jika ada error

echo "======================================="
echo "  Twitter Downloader Bot - Termux Setup"
echo "======================================="
echo ""

# 1. Update packages
echo "[1/5] Update packages Termux..."
pkg update -y && pkg upgrade -y

# 2. Install system deps
echo "[2/5] Install dependencies sistem..."
pkg install python python-pip git ffmpeg clang libxml2 libxslt -y

# 3. Upgrade pip
echo "[3/5] Upgrade pip..."
pip install --upgrade pip

# 4. Install Python packages
echo "[4/5] Install Python packages..."
pip install -r requirements.txt

# 5. Setup .env
echo "[5/5] Setup file .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "File .env berhasil dibuat dari template."
    echo "Sekarang edit file .env dan isi variabel yang diperlukan:"
    echo ""
    echo "  nano .env"
    echo ""
    echo "Variabel yang wajib diisi:"
    echo "  BOT_TOKEN         = token dari @BotFather"
    echo "  TWITTER_AUTH_TOKEN = cookie auth_token dari twitter.com"
    echo "  TWITTER_CT0        = cookie ct0 dari twitter.com"
else
    echo "File .env sudah ada, skip."
fi

echo ""
echo "======================================="
echo "  Setup selesai!"
echo "======================================="
echo ""
echo "Jalankan bot dengan:"
echo "  python bot.py"
echo ""
echo "Atau jalankan di background dengan tmux:"
echo "  pkg install tmux -y"
echo "  tmux new -s twitterbot 'python bot.py'"
echo ""
