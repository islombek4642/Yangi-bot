import logging
import asyncio
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Import handlers
from handlers import commands, messages, callbacks
from logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    admin_id = os.getenv("ADMIN_ID")
    if not admin_id:
        logger.warning("ADMIN_ID not set, cannot send error notification.")
        return

    # Don't send notification for common errors we can ignore
    if "Timed out" in str(context.error):
        return

    update_str = update.to_json() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {update_str}</pre>\n"
        f"<pre>context.chat_data = {str(context.chat_data)}</pre>\n"
        f"<pre>context.user_data = {str(context.user_data)}</pre>\n"
        f"<pre>{context.error}</pre>"
    )

    await context.bot.send_message(chat_id=admin_id, text=message, parse_mode="HTML")


def main() -> None:
    """Start the bot."""
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.critical("BOT_TOKEN environment variable not set!")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # --- Register all handlers here ---
    application.add_error_handler(error_handler)

    # Command handlers
    application.add_handler(CommandHandler("start", commands.start))
    application.add_handler(CommandHandler("stats", commands.stats))

    # Message handlers
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND, messages.handle_text
        )
    )
    application.add_handler(
        MessageHandler(
            filters.AUDIO | filters.VOICE | filters.VIDEO, messages.handle_media
        )
    )

    # Callback query handler
    application.add_handler(CallbackQueryHandler(callbacks.handle_callback))
    # --- End of handlers ---

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
