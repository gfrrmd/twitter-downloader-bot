"""Twitter media downloader menggunakan yt-dlp"""

import os
import asyncio
import logging
import tempfile
from typing import Optional, Dict, Any

import yt_dlp
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def _get_ytdlp_opts(extra: dict = None) -> dict:
    """
    Bangun konfigurasi yt-dlp dengan cookie Twitter.
    Cookie auth_token + ct0 diperlukan untuk konten age-restricted.
    """
    auth_token = os.getenv("TWITTER_AUTH_TOKEN", "")
    ct0 = os.getenv("TWITTER_CT0", "")

    opts = {
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        # Inject cookie Twitter untuk bypass age-restriction
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Cookie": f"auth_token={auth_token}; ct0={ct0};",
            "x-csrf-token": ct0,
            "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        },
        "extractor_args": {
            "twitter": {
                "api": ["graphql"],  # Gunakan GraphQL API (lebih reliable untuk age-restricted)
            }
        },
    }

    if extra:
        opts.update(extra)

    return opts


def _format_filesize(size_bytes: Optional[int]) -> str:
    """Format ukuran file ke string yang readable"""
    if not size_bytes:
        return "unknown"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / 1024 / 1024:.1f} MB"


class TwitterDownloader:
    """Wrapper async untuk yt-dlp Twitter downloader"""

    async def get_media_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Ambil informasi media dari URL tweet (tanpa download)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_info_sync, url)

    def _get_info_sync(self, url: str) -> Optional[Dict[str, Any]]:
        opts = _get_ytdlp_opts({"skip_download": True})

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

            if not info:
                return None

            # Tentukan tipe media
            ext = info.get("ext", "")
            vcodec = info.get("vcodec", "")
            acodec = info.get("acodec", "")

            if vcodec == "none" and acodec == "none":
                media_type = "photo"
            elif ext in ("gif",) or (vcodec != "none" and not info.get("duration")):
                media_type = "gif"
            else:
                media_type = "video"

            # Kumpulkan format yang tersedia
            formats = []
            for fmt in info.get("formats", [info]):
                if fmt.get("vcodec", "none") == "none":
                    continue
                height = fmt.get("height") or 0
                quality = (
                    f"{height}p" if height
                    else fmt.get("format_note", fmt.get("format_id", "unknown"))
                )
                formats.append({
                    "format_id": fmt.get("format_id", ""),
                    "quality": quality,
                    "ext": fmt.get("ext", "mp4"),
                    "filesize": fmt.get("filesize") or fmt.get("filesize_approx"),
                    "filesize_str": _format_filesize(
                        fmt.get("filesize") or fmt.get("filesize_approx")
                    ),
                    "url": fmt.get("url", ""),
                })

            # Sort by kualitas (tertinggi dulu)
            formats.sort(
                key=lambda x: int(x["quality"].rstrip("p")) if x["quality"].endswith("p") else 0,
                reverse=True
            )

            return {
                "type": media_type,
                "title": info.get("description") or info.get("title") or "Twitter Media",
                "uploader": info.get("uploader", ""),
                "thumbnail": info.get("thumbnail", ""),
                "duration": info.get("duration"),
                "formats": formats,
                "url": url,
                "raw": info,
            }

        except yt_dlp.utils.DownloadError as e:
            logger.error(f"yt-dlp DownloadError: {e}")
            raise ValueError(f"Gagal mengambil info: {str(e)}")
        except Exception as e:
            logger.error(f"Error tidak terduga: {e}", exc_info=True)
            raise

    async def download(self, url: str, info: Dict[str, Any],
                       format_id: str = None) -> Optional[str]:
        """Download media dan return path file sementara"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._download_sync, url, info, format_id
        )

    def _download_sync(self, url: str, info: Dict[str, Any],
                       format_id: str = None) -> Optional[str]:
        tmp_dir = tempfile.mkdtemp()
        output_template = os.path.join(tmp_dir, "%(id)s.%(ext)s")

        # Pilih format terbaik jika tidak ditentukan
        if format_id:
            fmt = format_id
        elif info.get("type") == "photo":
            fmt = "best"
        else:
            # Ambil kualitas tertinggi yang tersedia
            formats = info.get("formats", [])
            fmt = formats[0]["format_id"] if formats else "best"

        opts = _get_ytdlp_opts({
            "outtmpl": output_template,
            "format": fmt,
            "merge_output_format": "mp4",
        })

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            # Cari file yang didownload
            for filename in os.listdir(tmp_dir):
                if not filename.endswith(".part"):
                    return os.path.join(tmp_dir, filename)

            return None

        except Exception as e:
            logger.error(f"Gagal download {url}: {e}", exc_info=True)
            raise
