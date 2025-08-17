"""
Configuration file for the Telegram YouTube Transcript Bot
"""
import os

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token_here")

# Messages
WELCOME_MESSAGE = """
Hello! 👋

🎬 Welcome to YouTube Transcript Bot!

Send me a YouTube video link and I'll extract the transcript with timestamps for you.

Commands:
/start - Start the bot
/help - Show this help message

Just paste any YouTube URL and I'll do the rest! 📝
"""

HELP_MESSAGE = """
🔧 How to use this bot:

1. Send me a YouTube video link (any format)
2. I'll extract the transcript with timestamps
3. You'll receive a downloadable .txt file

Supported URL formats:
• https://www.youtube.com/watch?v=VIDEO_ID
• https://youtu.be/VIDEO_ID
• https://youtube.com/watch?v=VIDEO_ID
• https://m.youtube.com/watch?v=VIDEO_ID

Note: Only videos with available transcripts/subtitles can be processed.
"""

PROCESSING_MESSAGE = "🔄 Processing your video... Please wait..."
ERROR_NO_TRANSCRIPT = "❌ Sorry, this video doesn't have any available transcripts or subtitles."
ERROR_INVALID_URL = "❌ Please send a valid YouTube video URL."
ERROR_GENERAL = "❌ An error occurred while processing the video. Please try again."
SUCCESS_MESSAGE = "✅ Transcript extracted successfully! Here's your file:"
