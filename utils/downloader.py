import yt_dlp
import logging
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "vortex_bot"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def download_video(self, url: str) -> Optional[Dict]:
        """Download video from URL using yt-dlp."""
        try:
            ydl_opts = {
                'format': 'bestvideo*+bestaudio/best',
                'outtmpl': str(self.temp_dir / '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'verbose': True,  # Enable verbose logging for debugging
                'noplaylist': True,
                'concurrent_fragment_downloads': 4,
                'max_filesize': 50 * 1024 * 1024,  # 50MB limit
                'max_duration': 600,  # 10 minutes limit
                'merge_output_format': 'mp4', # Ensure merging into mp4
            }

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True)
            )

            if result:
                return {
                    'filename': result['requested_downloads'][0]['_filename'],
                    'title': result.get('title', 'Unknown'),
                    'duration': result.get('duration', 0),
                    'thumbnail': result.get('thumbnail')
                }
            return None

        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            return None

    async def download_audio(self, url: str, title: str) -> Optional[Dict]:
        """Download audio from URL using yt-dlp."""
        try:
            ydl_opts = self._get_ydl_opts(self.temp_dir / f'{title}.%(ext)s', is_audio=True)

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True)
            )

            if result:
                return {
                    'filename': result['requested_downloads'][0]['_filename'],
                    'title': result.get('title', 'Unknown'),
                    'duration': result.get('duration', 0)
                }
            return None

        except Exception as e:
            logger.error(f"Error downloading audio: {str(e)}")
            return None

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Progress hook for download status updates."""
        if d['status'] == 'downloading':
            logger.info(f"Downloading {d.get('filename', 'unknown')}... {d.get('_percent_str', '0%')} {d.get('_eta_str', '00:00')} remaining")
        elif d['status'] == 'finished':
            logger.info(f"Downloaded {d.get('filename', 'unknown')}")

    async def cleanup(self) -> None:
        """Cleanup temporary files."""
        try:
            for file in self.temp_dir.glob('*'):
                try:
                    file.unlink()
                except:
                    pass
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {str(e)}")

# Create a singleton instance
downloader = Downloader()
