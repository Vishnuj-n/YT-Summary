import os
from dotenv import load_dotenv

import yt_dlp
import requests
import base64
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# Load environment variables from .env file
load_dotenv()

# Initialize the LangChain Gemini client
# Make sure to set GOOGLE_API_KEY environment variable
def get_llm():
    """Initialize and return the LangChain Gemini client."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.3,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

MODEL_NAME = "gemini-2.5-flash"  # Updated to match the model in gemini.py
PROMPT = (
    "You are an expert content summarizer. Analyze the following transcript and create a comprehensive summary with these components:\n\n"
    "## Summary\n"
    "Provide a detailed yet concise summary (300-500 words) that captures the main narrative, key arguments, and important context.\n\n"
    "## Key Points\n"
    "* Extract all essential concepts or takeaways as bullet points\n"
    "* Focus on ideas that represent the core message\n"
    "* Include any notable quotes, statistics, or examples mentioned\n\n"
    "## Detailed Breakdown\n"
    "Organize the content into logical sections with appropriate subheadings\n\n"
    "## Questions & Answers\n"
    "Create 5 thoughtful Q&A pairs that:\n"
    "* Test understanding of critical concepts\n"
    "* Include both factual and analytical questions\n"
    "* Provide comprehensive answers\n\n"
    "## Key Terminology\n"
    "List and define 3-5 important terms or concepts introduced\n\n"
    "Format everything in clean, properly structured Markdown with clear headings, bullet points, and proper spacing."
)

def get_transcript(url):
    """Extract English subtitles (manual or auto) using yt_dlp and return plain text."""
    ydl_opts = {
        "quiet": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "subtitlesformat": "json3",
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            return None, f"❌ yt_dlp failed: {e}"

        subtitles = info.get("subtitles") or {}
        auto_subs = info.get("automatic_captions") or {}

        if "en" in subtitles:
            caption_url = subtitles["en"][0]["url"]
        elif "en" in auto_subs:
            caption_url = auto_subs["en"][0]["url"]
        else:
            return None, "❌ No English subtitles or captions found."

        try:
            response = requests.get(caption_url)
            data = response.json()
            transcript = "\n".join(
                event["segs"][0]["utf8"] for event in data["events"] if "segs" in event
            )
            return transcript.strip(), None
        except Exception as e:
            return None, f"❌ Failed to download or parse subtitles: {e}"

def summarize_transcript(transcript: str) -> str:
    """Call Gemini API to summarize transcript using LangChain."""
    try:
        # Initialize the LLM with API key
        llm = get_llm()
        
        # Create the message with the prompt and transcript
        message = HumanMessage(content=PROMPT + "\n\n" + transcript)
        
        # Get response from the LLM
        response = llm.invoke([message])
        
        return response.content
    except Exception as e:
        return f"❌ Failed to generate summary: {e}"

def download_markdown(markdown_content, filename=None):
    """
    Generate a download link for markdown content
    
    Args:
        markdown_content: The markdown content to download
        filename: Optional custom filename, defaults to timestamp-based name
        
    Returns:
        HTML string with download link
    """
    if not filename:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.md"
    
    # Encode markdown content to base64
    b64 = base64.b64encode(markdown_content.encode()).decode()
    
    # Create the download link HTML
    href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}" class="download-button">Download Summary as Markdown</a>'
    
    return href

