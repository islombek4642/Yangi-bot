import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.database import db
from utils.downloader import downloader
from utils.recognizer import music_recognizer
from utils.transcriber import transcriber

logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries."""
    query = update.callback_query
    data = query.data
    
    # Answer query
    await query.answer()
    
    try:
        # Handle different callback types
        if data == 'video':
            await handle_video_callback(query)
        elif data == 'music':
            await handle_music_callback(query)
        elif data == 'transcribe':
            await handle_transcribe_callback(query)
        elif data.startswith('download_music:'):
            await handle_download_music_callback(query, data)
        
    except Exception as e:
        logger.error(f"Error handling callback: {str(e)}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")

async def handle_video_callback(query) -> None:
    """Handle video callback."""
    await query.edit_message_text(
        "Video yuklash uchun quyidagi havolani yuboring:\n"
        "• YouTube video havolasi\n"
        "• Instagram video havolasi\n"
        "• TikTok video havolasi"
    )

async def handle_music_callback(query) -> None:
    """Handle music callback."""
    await query.edit_message_text(
        "Musiqa aniqlash uchun quyidagi fayllardan birini yuboring:\n"
        "• Ovozli xabar\n"
        "• Audio fayl\n"
        "• Video fayl"
    )

async def handle_transcribe_callback(query) -> None:
    """Handle transcription callback."""
    await query.edit_message_text(
        "Ovozni matnga o'girish uchun quyidagi fayllardan birini yuboring:\n"
        "• Ovozli xabar\n"
        "• Audio fayl\n"
        "• Video fayl"
    )

async def handle_download_music_callback(query, data: str) -> None:
    """Handle music download callback."""
    try:
        # Extract URL from callback data
        url = data.replace('download_music:', '')
        
        # Download audio
        music_info = await music_recognizer.search_music(url)
        if not music_info:
            await query.edit_message_text("❌ Qo'shiq topilmadi")
            return
        
        # Download audio
        audio_info = await downloader.download_audio(
            music_info['url'],
            f"{music_info['title']} - {music_info['artist']}"
        )
        
        if audio_info:
            await query.message.reply_audio(
                InputFile(audio_info['filename']),
                title=music_info['title'],
                performer=music_info['artist']
            )
        else:
            await query.edit_message_text("❌ Qo'shiq yuklanishda xatolik yuz berdi")
            
    except Exception as e:
        logger.error(f"Error downloading music: {str(e)}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
