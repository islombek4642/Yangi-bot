import logging
from pathlib import Path
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message, InputFile, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from utils.database import db
from utils.downloader import downloader
from utils.recognizer import music_recognizer
from utils.transcriber import transcriber
from utils.helpers import helpers

logger = logging.getLogger(__name__)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle a text message, which could be a command or a URL."""
    await db.add_user(update.effective_user)
    message = update.message
    text = message.text
    
    # Check if it's a URL
    if text.startswith(('http://', 'https://')):
        await process_url(message, text)
    else:
        await message.reply_text("📝 Matnli xabarlarni qabul qilishni hali qo'llab-quvvatlamayman.")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle audio, voice, and video messages."""
    await db.add_user(update.effective_user)
    message = update.message
    user = message.from_user
    
    # Log action
    await db.log_action(user.id, 'media')
    
    # Get file info
    file_info = None
    if message.audio:
        file_info = message.audio
    elif message.voice:
        file_info = message.voice
    elif message.video:
        file_info = message.video
    
    if not file_info:
        await message.reply_text("❌ Foydalanuvchi xatoligi: Foydalanuvchi xabari tushuntirilmagan")
        return
    
    try:
        # Download file
        file = await context.bot.get_file(file_info.file_id)
        file_path = await file.download_to_drive()
        
        # Validate file
        validation = helpers.validate_file(
            Path(file_path),
            max_size=25 * 1024 * 1024,  # 25MB
            max_duration=300  # 5 minutes
        )
        
        if not validation['valid']:
            await message.reply_text("❌ Xatolik: " + ". ".join(validation['errors']))
            return
        
        # Process based on file type
        try:
            if message.audio or message.voice:
                await process_audio(message, file_path)
            elif message.video:
                await process_video(message, file_path)
        finally:
            await downloader.cleanup_file(file_path)
        
    except Exception as e:
        logger.error(f"Error processing media: {str(e)}")
        await message.reply_text("❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")

async def process_url(message: Message, url: str) -> None:
    """Process URL message."""
    status_message = await message.reply_text("⏳ Havolani tekshirmoqdaman...")
    video_info = None  # Initialize video_info to None
    try:
        # Download video
        await status_message.edit_text("⏳ Videoni yuklab olmoqdaman...")
        video_info = await downloader.download_video(url)

        if not video_info:
            await status_message.edit_text(
                "❌ Havoladan video yuklab bo'lmadi.\n\n"
                "Instagram kabi ba'zi saytlar havoladan to'g'ridan-to'g'ri yuklashni cheklashi mumkin. "
                "Iltimos, videoni fayl sifatida yuboring."
            )
            return

        # Recognize music
        await status_message.edit_text("🎵 Musiqani qidirmoqdaman...")
        music_info = await music_recognizer.recognize_music(Path(video_info['filename']))

        # Delete status message
        await status_message.delete()

        # Send video
        await message.reply_video(
            InputFile(video_info['filename']),
            caption=f"✅ Video muvaffaqiyatli yuklandi: {video_info['title']}"
        )

        # If music found, send info with download button
        if music_info:
            keyboard = [
                [InlineKeyboardButton(
                    "✅ Qo'shiqni yuklash",
                    url=music_info['url']
                )]
            ]
            await message.reply_text(
                f"🎵 Qo'shiq topildi: {music_info['title']} - {music_info['artist']}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # If no music, try to transcribe
            await message.reply_text("📝 Videodagi nutq matnga o'girilmoqda...")
            transcript = await transcriber.transcribe_audio(Path(video_info['filename']))
            if transcript:
                await message.reply_text(f"📝 Transkripsiya natijasi:\n\n{transcript}")
            else:
                await message.reply_text("ℹ️ Ushbu videoda taniqli musiqa yoki nutq topilmadi.")

    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        await message.reply_text("❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
    finally:
        # Cleanup downloaded file
        if 'video_info' in locals() and video_info and 'filename' in video_info:
            await downloader.cleanup_file(video_info['filename'])

async def process_audio(message: Message, file_path: str) -> None:
    """Process audio/voice message."""
    try:
        # First try to recognize music
        await message.reply_text("🎵 Musiqani qidirmoqdaman...")
        music_info = await music_recognizer.recognize_music(Path(file_path))
        
        if music_info:
            # Try to find and download the music
            await message.reply_text("🎵 Qo'shiq topildi. Yuklanmoqda...")
            
            # Download audio
            audio_info = await downloader.download_audio(
                music_info['url'],
                f"{music_info['title']} - {music_info['artist']}"
            )
            
            if audio_info:
                await message.reply_audio(
                    InputFile(audio_info['filename']),
                    title=music_info['title'],
                    performer=music_info['artist']
                )
            else:
                await message.reply_text("❌ Qo'shiq yuklanishda xatolik yuz berdi")
        else:
            # If no music found, try transcription
            await message.reply_text("📝 Matnga o'girilmoqda...")
            transcript = await transcriber.transcribe_audio(Path(file_path))
            
            if transcript:
                await message.reply_text(f"📝 Transkripsiya natijasi:\n\n{transcript}")
            else:
                await message.reply_text("❌ Transkripsiya qilishda xatolik yuz berdi")
                
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        await message.reply_text("❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")

async def process_video(message: Message, file_path: str) -> None:
    """Process video message."""
    try:
        # First try to recognize music
        await message.reply_text("🎵 Musiqani qidirmoqdaman...")
        music_info = await music_recognizer.recognize_music(Path(file_path))
        
        if music_info:
            # Try to find and download the music
            await message.reply_text("🎵 Qo'shiq topildi. Yuklanmoqda...")
            
            # Download audio
            audio_info = await downloader.download_audio(
                music_info['url'],
                f"{music_info['title']} - {music_info['artist']}"
            )
            
            if audio_info:
                await message.reply_audio(
                    InputFile(audio_info['filename']),
                    title=music_info['title'],
                    performer=music_info['artist']
                )
            else:
                await message.reply_text("❌ Qo'shiq yuklanishda xatolik yuz berdi")
        else:
            # If no music found, try transcription
            await message.reply_text("📝 Matnga o'girilmoqda...")
            transcript = await transcriber.transcribe_audio(Path(file_path))
            
            if transcript:
                await message.reply_text(f"📝 Transkripsiya natijasi:\n\n{transcript}")
            else:
                await message.reply_text("❌ Transkripsiya qilishda xatolik yuz berdi")
                
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        await message.reply_text("❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming contact message."""
    contact = update.message.contact
    user = update.effective_user

    # Ensure the user is added to the DB before saving the phone number
    await db.add_user(user)

    if contact.user_id != user.id:
        await update.message.reply_text("Iltimos, o'zingizning kontaktingizni yuboring.")
        return

    await db.save_phone_number(user.id, contact.phone_number)
    
    await update.message.reply_text(
        "Rahmat! Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\nEndi musiqalarni aniqlash, videolardan audio ajratib olish va ovozli xabarlarni matnga o'girish uchun fayllarni yuborishingiz mumkin.",
        reply_markup=ReplyKeyboardRemove()
    )
