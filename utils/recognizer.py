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

    async def recognize_music(self, audio_path: Path) -> Optional[Dict]:
        """Recognize music from audio file using Shazam."""
        try:
            logger.info(f"Starting music recognition for {audio_path}")
            
            # Get audio signature
            out_signature = await self.shazam.create_signature(audio_path)
            
            if out_signature:
                # Search for music
                result = await self.shazam.recognize_song(out_signature)
                
                if result and result.get('track'):
                    track = result['track']
                    return {
                        'title': track.get('title', 'Unknown'),
                        'artist': track.get('subtitle', 'Unknown'),
                        'image': track.get('images', {}).get('coverart'),
                        'url': track.get('url')
                    }
            
            logger.info("No music recognized")
            return None

        except Exception as e:
            logger.error(f"Error recognizing music: {str(e)}")
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
