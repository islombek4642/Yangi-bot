# VortexFetchBot

Telegram bot that provides multiple services including video downloading, music recognition, and voice transcription.

## Features

- Video downloading from various platforms (YouTube, Instagram, TikTok)
- Music recognition from audio/video files
- Voice transcription using Whisper AI
- User-friendly interface with buttons and progress indicators
- MySQL database integration for user management and statistics
- Production-ready with Railway deployment support

## Requirements

- Python 3.10+
- MySQL 8.0+
- ffmpeg (for audio processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/VortexFetchBot.git
cd VortexFetchBot
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill in the required values:
```bash
cp .env.example .env
```

5. Edit `.env` with your configuration:
- `BOT_TOKEN`: Your Telegram bot token
- `ADMIN_ID`: Your Telegram user ID for /stats command
- MySQL database credentials

## Running Locally

```bash
python bot.py
```

## Deployment

The bot is configured for Railway deployment. Ensure you have:

1. A Railway account
2. MySQL database instance
3. Bot token and admin ID set in Railway variables

## Usage

1. Start the bot and send `/start` command
2. Share your contact when prompted
3. Use the bot's services:
   - Send video URLs to download
   - Send audio files to recognize music
   - Send voice messages to transcribe

## Error Handling

All errors are logged to `logs/bot.log`. The bot provides user-friendly error messages and continues to function even if individual operations fail.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
