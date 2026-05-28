"""Telegram bot handlers"""

import re
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction
from downloader import TwitterDownloader

logger = logging.getLogger(__name__)

TWITTER_URL_PATTERN = re.compile(
    r'https?://(?:www\.)?(?:twitter\.com|x\.com)/\w+/status/\d+',
    re.IGNORECASE
)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    text = (
        f"👋 Halo, <b>{user.first_name}</b>!\n\n"
        "🐦 <b>Twitter/X Downloader Bot</b>\n\n"
        "Kirimkan link tweet dan aku akan download medianya untuk kamu.\n\n"
        "📌 <b>Format URL yang didukung:</b>\n"
        "• <code>https://twitter.com/user/status/ID</code>\n"
        "• <code>https://x.com/user/status/ID</code>\n\n"
        "🎬 Support video, GIF, dan gambar\n\n"
        "Ketik /help untuk bantuan lebih lanjut."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    text = (
        "📖 <b>Cara Menggunakan Bot</b>\n\n"
        "1. Salin link tweet dari Twitter/X\n"
        "2. Paste dan kirim ke bot ini\n"
        "3. Tunggu bot memproses\n"
        "4. Pilih kualitas jika ada beberapa pilihan\n\n"
        "⚠️ <b>Batasan:</b>\n"
        f"• Ukuran file maksimal: {os.getenv('MAX_FILE_SIZE', 50)} MB\n"
        "• Hanya URL Twitter/X yang valid\n"
        "• Hanya konten publik yang dapat didownload"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with Twitter URLs"""
    message = update.message
    text = message.text.strip()

    # Cari URL Twitter di pesan
    match = TWITTER_URL_PATTERN.search(text)
    if not match:
        await message.reply_text(
            "❌ Tidak ada URL Twitter/X yang valid.\n"
            "Contoh: <code>https://x.com/user/status/123456789</code>",
            parse_mode=ParseMode.HTML
        )
        return

    url = match.group(0)
    status_msg = await message.reply_text("⏳ Sedang memproses URL...")

    try:
        await message.chat.send_action(ChatAction.TYPING)

        downloader = TwitterDownloader()
        info = await downloader.get_media_info(url)

        if not info:
            await status_msg.edit_text("❌ Gagal mengambil informasi media. Pastikan URL valid.")
            return

        media_type = info.get("type")
        title = info.get("title", "Twitter Media")

        if media_type == "video" and len(info.get("formats", [])) > 1:
            # Tampilkan pilihan kualitas
            keyboard = []
            for fmt in info["formats"]:
                label = f"{fmt['quality']} ({fmt['filesize_str']})"
                keyboard.append([InlineKeyboardButton(
                    label,
                    callback_data=f"dl:{fmt['format_id']}:{url}"
                )])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await status_msg.edit_text(
                f"🎬 <b>{title[:50]}</b>\n\nPilih kualitas video:",
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            # Simpan info di context untuk callback
            context.user_data["media_info"] = info
        else:
            # Langsung download
            await status_msg.edit_text("⬇️ Sedang mendownload...")
            await _send_media(update, context, status_msg, url, info)

    except ValueError as e:
        err = str(e)
        if "No video could be found" in err:
            await status_msg.edit_text(
                "❌ Tidak ada media di tweet ini.\n"
                "Bot hanya bisa download tweet yang mengandung video atau GIF."
            )
        else:
            await status_msg.edit_text(
                f"❌ Terjadi kesalahan: <code>{err[:200]}</code>",
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Error saat download {url}: {e}", exc_info=True)
        await status_msg.edit_text(
            f"❌ Terjadi kesalahan: <code>{str(e)[:200]}</code>",
            parse_mode=ParseMode.HTML
        )


async def _send_media(update, context, status_msg, url, info):
    """Download dan kirim media ke chat"""
    message = update.message or update.callback_query.message
    max_size = int(os.getenv("MAX_FILE_SIZE", 50)) * 1024 * 1024

    downloader = TwitterDownloader()
    filepath = None

    try:
        await status_msg.edit_text("📥 Mendownload file...")
        filepath = await downloader.download(url, info)

        if not filepath or not os.path.exists(filepath):
            await status_msg.edit_text("❌ File gagal didownload.")
            return

        file_size = os.path.getsize(filepath)
        if file_size > max_size:
            await status_msg.edit_text(
                f"❌ File terlalu besar ({file_size // 1024 // 1024}MB). "
                f"Batas maksimal {max_size // 1024 // 1024}MB."
            )
            return

        await status_msg.edit_text("📤 Mengirim file...")
        media_type = info.get("type")
        caption = f"🐦 <a href='{url}'>Sumber</a>"

        with open(filepath, "rb") as f:
            if media_type == "photo":
                await message.reply_photo(f, caption=caption, parse_mode=ParseMode.HTML)
            elif media_type in ("video", "gif"):
                await message.reply_video(f, caption=caption, parse_mode=ParseMode.HTML,
                                          supports_streaming=True)
            else:
                await message.reply_document(f, caption=caption, parse_mode=ParseMode.HTML)

        await status_msg.delete()

    finally:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
