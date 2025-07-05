import logging
import os
from typing import Optional, Dict
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)

class Helpers:
    @staticmethod
    def get_file_info(file_path: Path) -> Optional[Dict]:
        """Get file information (size, type, duration)."""
        try:
            if not file_path.exists():
                return None

            file_info = {
                'size': file_path.stat().st_size,
                'type': mimetypes.guess_type(str(file_path))[0],
                'name': file_path.name
            }

            # Get duration for audio/video files
            if file_info['type'] and ('audio' in file_info['type'] or 'video' in file_info['type']):
                import subprocess
                try:
                    result = subprocess.run([
                        'ffprobe',
                        '-v', 'quiet',
                        '-show_streams',
                        '-select_streams', 'a',
                        '-of', 'default=noprint_wrappers=1:nokey=1',
                        '-show_entries', 'stream=duration',
                        str(file_path)
                    ], capture_output=True, text=True)
                    
                    duration = float(result.stdout.strip())
                    file_info['duration'] = duration
                except:
                    pass

            return file_info
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return None

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to HH:MM:SS format."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def validate_file(file_path: Path, max_size: int, max_duration: float) -> Dict:
        """Validate file size and duration."""
        file_info = Helpers.get_file_info(file_path)
        if not file_info:
            return {'valid': False, 'error': 'File not found'}

        errors = []
        
        if file_info['size'] > max_size:
            errors.append(f"File too large ({Helpers.format_file_size(file_info['size'])}). Maximum size: {Helpers.format_file_size(max_size)}")
        
        if 'duration' in file_info and file_info['duration'] > max_duration:
            errors.append(f"File too long ({Helpers.format_duration(file_info['duration'])}). Maximum duration: {Helpers.format_duration(max_duration)}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'info': file_info
        }

# Create a singleton instance
helpers = Helpers()
