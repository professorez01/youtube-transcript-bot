"""
YouTube utilities for transcript extraction and URL processing
"""
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from datetime import datetime
from io import StringIO


def extract_video_id(url):
    """
    Extract YouTube video ID from various URL formats
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|m\.youtube\.com\/watch\?v=)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def get_video_title(video_id):
    """
    Get video title using YouTube's oEmbed API
    """
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('title', f'Video_{video_id}')
    except:
        pass
    
    return f'Video_{video_id}'


def format_timestamp(seconds):
    """
    Convert seconds to MM:SS or HH:MM:SS format
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def get_youtube_transcript(video_id):
    """
    Extract transcript from YouTube video with timestamps
    """
    try:
        # Priority order: Hindi, English, then any available language
        language_priority = ['hi', 'hi-IN', 'en', 'en-US', 'en-GB']
        transcript_list = None
        found_language = None
        
        # Try to find transcript in priority order
        for lang in language_priority:
            try:
                transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=[lang])
                found_language = lang
                break
            except:
                continue
        
        # If no priority language found, try to get any available transcript
        if not transcript_list:
            try:
                # Try auto-generated transcript
                transcript_list = YouTubeTranscriptApi().fetch(video_id)
                found_language = 'auto-detected'
            except Exception as e:
                return None, f"No transcript available: {str(e)}"
        
        if not transcript_list:
            return None, "No transcript available"
        
        # Get video title
        video_title = get_video_title(video_id)
        
        # Format transcript with timestamps
        formatted_transcript = StringIO()
        formatted_transcript.write(f"Transcript for: {video_title}\n")
        formatted_transcript.write(f"Video ID: {video_id}\n")
        formatted_transcript.write(f"Language: {found_language or 'Unknown'}\n")
        formatted_transcript.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        formatted_transcript.write("=" * 60 + "\n\n")
        
        for entry in transcript_list:
            timestamp = format_timestamp(entry.start)
            text = entry.text.strip()
            formatted_transcript.write(f"[{timestamp}] {text}\n")
        
        # Generate filename
        safe_title = re.sub(r'[^\w\s-]', '', video_title)
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        filename = f"{safe_title}_{video_id}_{datetime.now().strftime('%Y%m%d')}.txt"
        
        return formatted_transcript.getvalue(), filename
        
    except Exception as e:
        return None, str(e)


def get_available_transcripts(video_id):
    """
    Get information about all available transcripts for a video
    """
    try:
        # Try different common language codes to see what's available
        common_languages = ['hi', 'hi-IN', 'en', 'en-US', 'en-GB', 'es', 'fr', 'de', 'ja', 'ko']
        available_transcripts = []
        
        for lang in common_languages:
            try:
                YouTubeTranscriptApi().fetch(video_id, languages=[lang])
                available_transcripts.append({
                    'language': lang,
                    'language_code': lang,
                    'is_generated': False,  # Can't determine without advanced API
                    'is_translatable': True
                })
            except:
                continue
        
        # Try auto-generated if no manual transcripts found
        if not available_transcripts:
            try:
                YouTubeTranscriptApi().fetch(video_id)
                available_transcripts.append({
                    'language': 'auto-detected',
                    'language_code': 'auto',
                    'is_generated': True,
                    'is_translatable': False
                })
            except:
                pass
        
        return available_transcripts
    except Exception as e:
        return []


def is_valid_youtube_url(url):
    """
    Check if the provided URL is a valid YouTube URL
    """
    youtube_patterns = [
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be|m\.youtube\.com)',
    ]
    
    for pattern in youtube_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    
    return False
