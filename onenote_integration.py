import os
from dotenv import load_dotenv
from auth_manager import AuthManager
from onenote_manager import OneNoteManager

# Load environment variables
load_dotenv()

def save_to_onenote(video_title, video_url, summary, transcript=None):
    """
    Save a video summary to OneNote.
    
    Args:
        video_title (str): Title of the YouTube video
        video_url (str): URL of the YouTube video
        summary (str): AI-generated summary content
        transcript (str, optional): Original transcript for preview
    
    Returns:
        tuple: (success: bool, message: str, page_url: str or None)
    """
    try:
        # Get Microsoft credentials
        client_id = os.getenv("MICROSOFT_CLIENT_ID")
        client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        
        if not client_id:
            return False, "❌ MICROSOFT_CLIENT_ID not found in environment variables", None
        
        # Get OneNote configuration
        notebook_name = os.getenv("ONENOTE_NOTEBOOK_NAME", "YouTube Summaries")
        section_name = os.getenv("ONENOTE_SECTION_NAME", "AI Generated Summaries")
        
        print("🔐 Authenticating with Microsoft...")
        
        # Initialize authentication
        auth = AuthManager(client_id, client_secret)
        access_token = auth.get_access_token()
        
        if not access_token:
            return False, "❌ Failed to get Microsoft access token", None
        
        print("✅ Authentication successful!")
        
        # Initialize OneNote manager
        onenote = OneNoteManager(access_token)
        
        # Get or create notebook and section
        notebook_id = onenote.get_or_create_notebook(notebook_name)
        section_id = onenote.get_or_create_section(notebook_id, section_name)
        
        # Create transcript preview
        transcript_preview = None
        if transcript:
            # Clean and truncate transcript for preview
            clean_transcript = ' '.join(transcript.split())  # Remove extra whitespace
            transcript_preview = clean_transcript[:500] if len(clean_transcript) > 500 else clean_transcript
        
        # Create the page
        page_id, page_url = onenote.create_summary_page(
            section_id, video_title, video_url, summary, transcript_preview
        )
        
        success_message = f"✅ Summary saved to OneNote successfully!"
        if page_url:
            success_message += f"\n🔗 View at: {page_url}"
        
        return True, success_message, page_url
        
    except Exception as e:
        error_message = f"❌ Failed to save to OneNote: {str(e)}"
        print(error_message)
        return False, error_message, None

def list_recent_summaries(count=5):
    """
    List recent summaries from OneNote.
    
    Args:
        count (int): Number of recent summaries to retrieve
        
    Returns:
        tuple: (success: bool, summaries: list, message: str)
    """
    try:
        # Get credentials
        client_id = os.getenv("MICROSOFT_CLIENT_ID")
        client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        
        if not client_id:
            return False, [], "❌ MICROSOFT_CLIENT_ID not found in environment variables"
        
        # Get configuration
        notebook_name = os.getenv("ONENOTE_NOTEBOOK_NAME", "YouTube Summaries")
        section_name = os.getenv("ONENOTE_SECTION_NAME", "AI Generated Summaries")
        
        # Authenticate
        auth = AuthManager(client_id, client_secret)
        access_token = auth.get_access_token()
        
        if not access_token:
            return False, [], "❌ Failed to authenticate with Microsoft"
        
        # Get OneNote data
        onenote = OneNoteManager(access_token)
        notebook_id = onenote.get_or_create_notebook(notebook_name)
        section_id = onenote.get_or_create_section(notebook_id, section_name)
        
        # Get recent pages
        pages = onenote.list_recent_pages(section_id, count)
        
        return True, pages, f"✅ Found {len(pages)} recent summaries"
        
    except Exception as e:
        error_message = f"❌ Failed to get summaries: {str(e)}"
        return False, [], error_message

def search_summaries(query):
    """
    Search for summaries in OneNote.
    
    Args:
        query (str): Search query
        
    Returns:
        tuple: (success: bool, results: list, message: str)
    """
    try:
        # Get credentials
        client_id = os.getenv("MICROSOFT_CLIENT_ID")
        client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        
        if not client_id:
            return False, [], "❌ MICROSOFT_CLIENT_ID not found in environment variables"
        
        # Get configuration
        notebook_name = os.getenv("ONENOTE_NOTEBOOK_NAME", "YouTube Summaries")
        
        # Authenticate
        auth = AuthManager(client_id, client_secret)
        access_token = auth.get_access_token()
        
        if not access_token:
            return False, [], "❌ Failed to authenticate with Microsoft"
        
        # Search
        onenote = OneNoteManager(access_token)
        notebook_id = onenote.get_or_create_notebook(notebook_name)
        results = onenote.search_pages(query, notebook_id)
        
        return True, results, f"✅ Found {len(results)} matching summaries"
        
    except Exception as e:
        error_message = f"❌ Search failed: {str(e)}"
        return False, [], error_message

def test_onenote_connection():
    """
    Test the OneNote connection and setup.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        print("🧪 Testing OneNote connection...")
        
        # Check environment variables
        client_id = os.getenv("MICROSOFT_CLIENT_ID")
        if not client_id:
            return False, "❌ MICROSOFT_CLIENT_ID not found in .env file"
        
        print("✅ Environment variables found")
        
        # Test authentication
        auth = AuthManager(client_id, os.getenv("MICROSOFT_CLIENT_SECRET"))
        access_token = auth.get_access_token()
        
        if not access_token:
            return False, "❌ Failed to authenticate with Microsoft"
        
        print("✅ Authentication successful")
        
        # Test OneNote access
        onenote = OneNoteManager(access_token)
        notebook_name = os.getenv("ONENOTE_NOTEBOOK_NAME", "YouTube Summaries")
        notebook_id = onenote.get_or_create_notebook(notebook_name)
        
        print(f"✅ OneNote access successful - Notebook ID: {notebook_id}")
        
        return True, "✅ OneNote connection test successful!"
        
    except Exception as e:
        return False, f"❌ Connection test failed: {str(e)}"
