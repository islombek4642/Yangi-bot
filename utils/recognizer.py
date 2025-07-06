import logging
import asyncio
from typing import Optional, Dict
import tempfile
from shazamio import Shazam
from pathlib import Path

logger = logging.getLogger(__name__)

class MusicRecognizer:
    def __init__(self):
        self.shazam = Shazam()
        self.temp_dir = Path(tempfile.gettempdir()) / "vortex_bot"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def recognize_music(self, file_path: Path) -> Optional[Dict]:
        """Recognize music from a media file by first extracting audio with ffmpeg."""
        logger.info(f"Starting music recognition for {file_path}")
        
        audio_file_to_process = file_path
        temp_audio_file = None

        video_extensions = ['.mp4', '.mkv', '.mov', '.avi', '.webm', '.m4v']
        if file_path.suffix.lower() in video_extensions:
            logger.info(f"Video file detected. Extracting audio with ffmpeg from {file_path}")
            temp_audio_file = self.temp_dir / f"{file_path.stem}.mp3"
            
            command = [
                'ffmpeg',
                '-i', str(file_path),
                '-vn',          # No video
                '-acodec', 'libmp3lame',
                '-q:a', '2',    # Audio quality
                '-y',           # Overwrite output
                str(temp_audio_file)
            ]

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"ffmpeg failed for {file_path}. Stderr: {stderr.decode()}")
                if temp_audio_file.exists():
                    temp_audio_file.unlink()
                return None
            
            logger.info(f"Audio extracted successfully to {temp_audio_file}")
            audio_file_to_process = temp_audio_file
        
        try:
            logger.info(f"Processing {audio_file_to_process} with Shazam.")
            out = await self.shazam.recognize(str(audio_file_to_process))

            if out and out.get('track'):
                track = out['track']
                logger.info(f"Music recognized: {track.get('title')} - {track.get('subtitle')}")
                return {
                    'title': track.get('title', 'N/A'),
                    'subtitle': track.get('subtitle', 'N/A'),
                    'url': track.get('share', {}).get('href')
                }
            else:
                logger.info(f"No music track found for {audio_file_to_process}")
                return None
                
        except Exception as e:
            logger.error(f"An exception occurred during Shazam recognition: {e}")
            return None
        finally:
            if temp_audio_file and temp_audio_file.exists():
                temp_audio_file.unlink()
                logger.info(f"Cleaned up temporary audio file: {temp_audio_file}")

    async def search_music(self, query: str) -> Optional[Dict]:
        """Search for music on YouTube using recognized track info."""
        try:
            # Search YouTube for the track
            results = await self.shazam.search(query)
            
            if results and results.get('tracks') and results['tracks'].get('hits'):
                # Get the first result
                track = results['tracks']['hits'][0]['track']
                return {
                    'title': track.get('title', 'Unknown'),
                    'artist': track.get('subtitle', 'Unknown'),
                    'url': track.get('url')
                }
            
            return None

        except Exception as e:
            logger.error(f"Error searching music: {str(e)}")
            return None

# Create a singleton instance
music_recognizer = MusicRecognizer()
