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
        """Recognize music from an audio file using the updated shazamio method."""
        logger.info(f"Starting music recognition for {file_path}")
        try:
            # The new shazamio `recognize` method takes the file path directly.
            out = await self.shazam.recognize(str(file_path))

            if out and out.get('track'):
                track = out['track']
                logger.info(f"Music recognized: {track.get('title')} - {track.get('subtitle')}")
                return {
                    'title': track.get('title', 'N/A'),
                    'subtitle': track.get('subtitle', 'N/A'),
                    'url': track.get('share', {}).get('href')
                }
            else:
                logger.info(f"No music track found in the recognition result for {file_path}")
                return None
        except Exception as e:
            logger.error(f"An exception occurred during music recognition: {e}")
            return None

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
