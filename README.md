# 🐦 Twitter Downloader Bot

Bot Telegram untuk download video/GIF/media dari Twitter/X, termasuk konten **age-restricted** (18+).

## ✨ Fitur

- ✅ Download video Twitter/X (MP4)
- ✅ Download GIF Twitter
- ✅ Download foto/gambar
- ✅ Support konten **age-restricted** (NSFW/18+)
- ✅ Pilih kualitas video (High/Medium/Low)
- ✅ Progress bar saat download
- ✅ Support URL `twitter.com` dan `x.com`
- ✅ Deploy-ready di Railway / VPS

## 🚀 Deploy ke Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. Fork repo ini
2. Buat project baru di [Railway](https://railway.app)
3. Connect ke repo yang sudah di-fork
4. Set environment variables (lihat bawah)
5. Deploy!

## ⚙️ Environment Variables

| Variable | Keterangan | Contoh |
|---|---|---|
| `BOT_TOKEN` | Token bot dari @BotFather | `123456:ABC-DEF...` |
| `TWITTER_AUTH_TOKEN` | Cookie `auth_token` Twitter (wajib untuk age-restricted) | `abc123...` |
| `TWITTER_CT0` | Cookie `ct0` (CSRF token) Twitter | `xyz789...` |
| `ADMIN_ID` | Telegram user ID admin (opsional) | `123456789` |
| `MAX_FILE_SIZE` | Batas ukuran file MB (default: 50) | `50` |

## 📦 Install Lokal

```bash
git clone https://github.com/gfrrmd/twitter-downloader-bot
cd twitter-downloader-bot
pip install -r requirements.txt
cp .env.example .env
# Edit .env dan isi variabel yang diperlukan
python bot.py
```

## 🍪 Cara Dapat Cookie Twitter (Untuk Age-Restricted)

1. Login ke [twitter.com](https://twitter.com) / [x.com](https://x.com)
2. Buka DevTools (F12) → Application → Cookies
3. Cari dan copy nilai:
   - `auth_token` → isi ke `TWITTER_AUTH_TOKEN`
   - `ct0` → isi ke `TWITTER_CT0`

> ⚠️ **Penting**: Gunakan akun Twitter yang sudah diverifikasi umur (18+) dan aktifkan "Display sensitive media" di settings.

## 📝 Cara Pakai Bot

1. Start bot dengan `/start`
2. Kirim link tweet, contoh:
   - `https://twitter.com/user/status/123456789`
   - `https://x.com/user/status/123456789`
3. Pilih kualitas video jika ada beberapa pilihan
4. Bot akan mengirimkan file media

## 🛠️ Tech Stack

- Python 3.10+
- [python-telegram-bot](https://python-telegram-bot.org/) v20+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) untuk ekstrak media
- [aiohttp](https://docs.aiohttp.org/) untuk async HTTP
- [tweepy](https://www.tweepy.org/) (opsional, untuk metadata)

## 📄 Lisensi

MIT License - lihat [LICENSE](LICENSE)
