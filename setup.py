from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vortexfetchbot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Telegram bot for video downloading, music recognition, and voice transcription",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/VortexFetchBot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=[
        'python-telegram-bot>=20.7',
        'shazamio>=3.0.0',
        'faster-whisper>=0.11.0',
        'yt-dlp>=2024.01.06',
        'mysql-connector-python>=8.2.0',
        'pydub>=0.25.1',
        'python-dotenv>=1.0.0',
        'aiofiles>=23.2.1',
        'aiosqlite>=0.19.0',
        'python-multipart>=0.0.6',
        'ffmpeg-python>=0.2.0'
    ],
    entry_points={
        'console_scripts': [
            'vortexfetchbot=bot:main',
        ],
    },
)
