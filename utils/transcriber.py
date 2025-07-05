import logging
import asyncio
import os
from typing import Optional, Dict
from faster_whisper import WhisperModel
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)

class Transcriber:
    def __init__(self):
        self.model = WhisperModel("base", device="cpu")  # Using CPU for better compatibility
        self.temp_dir = Path(tempfile.gettempdir()) / "vortex_bot"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit
        self.max_duration = 180  # 3 minutes limit in seconds

    async def transcribe_audio(self, audio_path: Path) -> Optional[str]:
        """Transcribe audio file to text using faster-whisper."""
        try:
            # Check file size
            if audio_path.stat().st_size > self.max_file_size:
                logger.warning(f"File too large: {audio_path}")
                return None

            # Check duration
            duration = self._get_audio_duration(audio_path)
            if duration > self.max_duration:
                logger.warning(f"Audio too long: {audio_path}")
                return None

            # Transcribe using faster-whisper
            segments, _ = await self.model.transcribe(audio_path, language="auto")
            
            # Join all segments
            transcript = " ".join([segment.text for segment in segments])
            
            logger.info(f"Transcribed {audio_path}: {len(transcript)} characters")
            return transcript

        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None

    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds using ffprobe."""
        try:
            import subprocess
            
            result = subprocess.run([
                'ffprobe',
                '-v', 'quiet',
                '-show_streams',
                '-select_streams', 'a',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                '-show_entries', 'stream=duration',
                str(audio_path)
            ], capture_output=True, text=True)
            
            duration = float(result.stdout.strip())
            return duration
            
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            return 0

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
transcriber = Transcriber()
