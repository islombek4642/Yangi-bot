import os
import unittest
from unittest.mock import AsyncMock, patch
from telegram import Update, Message, User, Audio, Voice, Video, Contact
from telegram.ext import ContextTypes
from bot import main
from handlers import commands, messages
from utils.database import Database
from utils.downloader import Downloader
from utils.recognizer import MusicRecognizer
from utils.transcriber import Transcriber
from utils.helpers import Helpers

class TestBot(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Mock database connection
        self.db = Database()
        self.db.pool = AsyncMock()
        self.db.pool.get_connection.return_value = AsyncMock()

        # Mock other utilities
        self.downloader = Downloader()
        self.recognizer = MusicRecognizer()
        self.transcriber = Transcriber()
        self.helpers = Helpers()

    async def test_start_command(self):
        # Create mock update
        user = User(id=123, first_name="Test", username="testuser", is_bot=False)
        message = Message(message_id=1, date=None, chat=None, from_user=user)
        update = Update(update_id=1, message=message)

        # Mock database response
        self.db.add_user.return_value = True
        self.db.get_user_stats.return_value = None

        # Call start command
        await commands.start(update, None)

        # Check database calls
        self.db.add_user.assert_called_once()

    async def test_handle_text_with_url(self):
        # Create mock update
        message = Message(message_id=1, date=None, chat=None, from_user=None)
        message.text = "https://youtube.com/watch?v=test"
        update = Update(update_id=1, message=message)

        # Mock downloader
        self.downloader.download_video.return_value = {
            'filename': 'test.mp4',
            'title': 'Test Video'
        }

        # Call handler
        await messages.handle_text(update, None)

        # Check calls
        self.downloader.download_video.assert_called_once()

    async def test_handle_audio(self):
        # Create mock update
        message = Message(message_id=1, date=None, chat=None, from_user=None)
        audio = Audio(file_id="test", file_unique_id="test", duration=10)
        message.audio = audio
        update = Update(update_id=1, message=message)

        # Mock recognizer
        self.recognizer.recognize_music.return_value = {
            'title': 'Test Song',
            'artist': 'Test Artist'
        }

        # Call handler
        await messages.handle_media(update, None)

        # Check calls
        self.recognizer.recognize_music.assert_called_once()

    async def test_handle_voice(self):
        # Create mock update
        message = Message(message_id=1, date=None, chat=None, from_user=None)
        voice = Voice(file_id="test", file_unique_id="test", duration=10)
        message.voice = voice
        update = Update(update_id=1, message=message)

        # Mock transcriber
        self.transcriber.transcribe_audio.return_value = "Test transcription"

        # Call handler
        await messages.handle_media(update, None)

        # Check calls
        self.transcriber.transcribe_audio.assert_called_once()

if __name__ == '__main__':
    unittest.main()
