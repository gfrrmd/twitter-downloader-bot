#!/usr/bin/env python3
"""Twitter Downloader Bot - Main entry point"""

import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import start_handler, help_handler, download_handler

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN tidak ditemukan di environment variables!")

    app = Application.builder().token(token).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        download_handler
    ))

    webhook_url = os.getenv("WEBHOOK_URL")
    port = int(os.getenv("PORT", 8080))

    if webhook_url:
        logger.info(f"Menjalankan bot dengan webhook: {webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url,
            url_path=token,
        )
    else:
        logger.info("Menjalankan bot dengan polling...")
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
