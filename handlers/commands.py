import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.database import db
from utils.helpers import helpers

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    
    # Check if user is new
    if not await db.get_user_stats(user.id):
        # Add user to database
        await db.add_user(
            user.id,
            user.first_name,
            user.username,
            user.phone_number
        )
        
        # Send welcome message with contact request
        keyboard = [
            [InlineKeyboardButton("Kontaktingizni yuborish", request_contact=True)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Assalomu alaykum, {user.first_name}!\n\n"
            "Men siz uchun quyidagi xizmatlarni taqdim etaman:\n"
            "• Video yuklash\n"
            "• Musiqa aniqlash\n"
            "• Ovozli xabarlarni matnga o'girish\n\n"
            "To'liq ishlash uchun, iltimos, kontaktingizni ulashing.",
            reply_markup=reply_markup
        )
    else:
        # Send welcome back message
        await update.message.reply_text(
            f"Xush kelibsiz, {user.first_name}!\n"
            "Quyidagi xizmatlardan foydalanishingiz mumkin:\n"
            "• Video yuklash\n"
            "• Musiqa aniqlash\n"
            "• Ovozli xabarlarni matnga o'girish",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Video yuklash", callback_data='video')],
                [InlineKeyboardButton("Musiqa aniqlash", callback_data='music')],
                [InlineKeyboardButton("Ovozni matnga o'girish", callback_data='transcribe')]
            ])
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
    """Handle contact sharing."""
    user = update.effective_user
    contact = update.message.contact
    
    # Update user's phone number
    await db.add_user(
        user.id,
        user.first_name,
        user.username,
        contact.phone_number
    )
    
    await update.message.reply_text(
        "Kontakt saqlandi! Quyidagi xizmatlardan foydalanishingiz mumkin:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Video yuklash", callback_data='video')],
            [InlineKeyboardButton("Musiqa aniqlash", callback_data='music')],
            [InlineKeyboardButton("Ovozni matnga o'girish", callback_data='transcribe')]
        ])
    )
