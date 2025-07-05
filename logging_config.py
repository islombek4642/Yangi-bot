import logging
from pathlib import Path

def setup_logging() -> None:
    """Configure logging for the application."""
    # 1. Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # 2. Define the log file path
    log_file = logs_dir / "bot.log"

    # 3. Configure logging
    # This will be the root logger configuration.
    # Any logger created with logging.getLogger(name) will inherit this.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'), # Log to a file
            logging.StreamHandler() # Log to the console
        ],
    )

    # Optional: Silence overly verbose loggers from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger('telegram.ext').setLevel(logging.WARNING)

