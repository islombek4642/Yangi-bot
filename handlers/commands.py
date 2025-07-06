import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.database import db
from utils.helpers import helpers

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command, ensuring user is fully registered."""
    user = update.effective_user
    
    # Check if user exists and has a phone number
    user_data = await db.get_user(user.id)
    
    if user_data and user_data.get('phone_number'):
        # User is fully registered, send welcome back message
        await update.message.reply_text(
            f"Xush kelibsiz, {user.first_name}!\n\nSiz botdan to'liq foydalanishingiz mumkin."
        )
    else:
        # New user or existing user without a phone number
        if not user_data:
            await db.add_user(user)
            logger.info(f"New user {user.id} added to the database.")

        # Send welcome message with contact request
        keyboard = [
            [KeyboardButton("📱 Kontaktni ulashish", request_contact=True)],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_html(
            text=f"Assalomu alaykum, {user.mention_html()}!\n\nBotdan to'liq foydalanish uchun, iltimos, <b>'Kontaktni ulashish'</b> tugmasini bosing.",
            reply_markup=reply_markup
        )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command."""
    # Only allow admin to see stats
    admin_id = int(os.getenv('ADMIN_ID', 0))
    if update.effective_user.id != admin_id:
        await update.message.reply_text("Bu buyruq faqat admin uchun")
        return

    # Get bot statistics
    stats = await db.get_bot_stats()
    
    await update.message.reply_text(
        f"📊 Bot Statistikasi:\n\n"
        f"👥 Umumiy foydalanuvchilar: {stats['total_users']}\n"
        f"🆕 Bugun qo'shilganlar: {stats['new_today']}\n"
        f"📊 Umumiy ishlatilgan xizmatlar: {stats['total_actions']}",
        parse_mode='Markdown'
    )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle contact sharing and complete registration."""
    user = update.effective_user
    contact = update.message.contact
    
    if contact:
        await db.update_phone_number(user.id, contact.phone_number)
        logger.info(f"User {user.id} shared their contact: {contact.phone_number}")
        
        # Remove the custom keyboard and send confirmation
        await update.message.reply_text(
            "Rahmat! Ro'yxatdan o'tish muvaffaqiyatli yakunlandi.\n\nEndi botning barcha imkoniyatlaridan foydalanishingiz mumkin.",
            reply_markup=None # Removes the keyboard
        )
    else:
        logger.warning(f"Contact handler called without a contact object from user {user.id}")
