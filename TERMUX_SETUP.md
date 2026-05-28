# 📱 Cara Deploy di Termux

## 1. Install Dependencies Termux

Buka Termux dan jalankan perintah berikut satu per satu:

```bash
# Update package list
pkg update && pkg upgrade -y

# Install Python dan dependencies sistem
pkg install python python-pip git ffmpeg -y

# Install compiler (diperlukan beberapa library)
pkg install clang libxml2 libxslt -y
```

## 2. Clone Repo

```bash
git clone https://github.com/gfrrmd/twitter-downloader-bot
cd twitter-downloader-bot
```

## 3. Install Python Packages

```bash
# Upgrade pip dulu
pip install --upgrade pip

# Install semua dependencies
pip install -r requirements.txt
```

> ⚠️ Jika ada error saat install `aiohttp`, coba:
> ```bash
> pip install aiohttp --no-build-isolation
> ```

## 4. Setup .env

```bash
cp .env.example .env
nano .env
```

Isi variabel berikut:
```
BOT_TOKEN=token_bot_kamu
TWITTER_AUTH_TOKEN=auth_token_dari_cookie
TWITTER_CT0=ct0_dari_cookie
```

Simpan: `Ctrl+X` → `Y` → Enter

## 5. Jalankan Bot

```bash
python bot.py
```

## 6. Jalankan di Background (agar tidak mati saat layar off)

```bash
# Install tmux
pkg install tmux -y

# Buat sesi baru
tmux new -s twitterbot

# Jalankan bot
python bot.py

# Detach dari sesi (bot tetap jalan)
# Tekan: Ctrl+B lalu D

# Untuk kembali ke sesi:
tmux attach -t twitterbot
```

## 🔄 Auto-restart jika crash

```bash
# Buat script loop
cat > run.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/twitter-downloader-bot
while true; do
    echo "[$(date)] Menjalankan bot..."
    python bot.py
    echo "[$(date)] Bot berhenti, restart dalam 5 detik..."
    sleep 5
done
EOF

chmod +x run.sh

# Jalankan dengan tmux
tmux new -s twitterbot './run.sh'
```

## 🛠️ Update Bot

```bash
cd ~/twitter-downloader-bot
git pull
pip install -r requirements.txt
```
