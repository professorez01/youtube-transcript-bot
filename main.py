"""
Telegram Bot for YouTube Transcript Extraction
This bot extracts YouTube video transcripts with timestamps and sends them as downloadable text files.
"""
import logging
import io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import *
from youtube_utils import extract_video_id, get_youtube_transcript, is_valid_youtube_url, get_available_transcripts

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command
    """
    await update.message.reply_text(WELCOME_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /help command
    """
    await update.message.reply_text(HELP_MESSAGE)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming messages containing YouTube URLs
    """
    message_text = update.message.text
    
    # Check if message contains a YouTube URL
    if not is_valid_youtube_url(message_text):
        await update.message.reply_text(
            "Please send a valid YouTube video URL.\n\n"
            "Example formats:\n"
            "• https://www.youtube.com/watch?v=VIDEO_ID\n"
            "• https://youtu.be/VIDEO_ID"
        )
        return
    
    # Extract video ID
    video_id = extract_video_id(message_text)
    if not video_id:
        await update.message.reply_text(ERROR_INVALID_URL)
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text(PROCESSING_MESSAGE)
    
    try:
        # Check available transcripts first
        available_transcripts = get_available_transcripts(video_id)
        
        # Extract transcript
        transcript_content, result = get_youtube_transcript(video_id)
        
        if transcript_content is None:
            # Show available transcripts if extraction failed
            if available_transcripts:
                transcript_info = "\n".join([
                    f"• {t['language']} ({t['language_code']}) - {'Auto-generated' if t['is_generated'] else 'Manual'}"
                    for t in available_transcripts[:5]  # Show first 5
                ])
                await processing_msg.edit_text(f"{ERROR_NO_TRANSCRIPT}\n\nAvailable transcripts:\n{transcript_info}\n\nError: {result}")
            else:
                await processing_msg.edit_text(f"{ERROR_NO_TRANSCRIPT}\n\nError: {result}")
            return
        
        # Create file buffer
        file_buffer = io.BytesIO(transcript_content.encode('utf-8'))
        file_buffer.seek(0)
        
        # Send the file
        await update.message.reply_document(
            document=file_buffer,
            filename=result,
            caption=SUCCESS_MESSAGE
        )
        
        # Delete processing message
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {str(e)}")
        await processing_msg.edit_text(f"{ERROR_GENERAL}\n\nError: {str(e)}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle errors
    """
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "An unexpected error occurred. Please try again later."
        )


def main():
    """
    Main function to run the bot
    """
    # Check if bot token is provided
    if BOT_TOKEN == "your_bot_token_here":
        print("Error: Please set the TELEGRAM_BOT_TOKEN environment variable")
        print("Get your bot token from @BotFather on Telegram")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Print startup message
    print("🤖 YouTube Transcript Bot is starting...")
    print(f"Bot token: {BOT_TOKEN[:10]}...")
    print("Send /start to begin using the bot!")
    
    # Run the bot
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")


if __name__ == "__main__":
    main()
