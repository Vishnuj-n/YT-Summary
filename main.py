import os
from datetime import datetime
from summary import get_transcript, summarize_transcript, download_markdown
from onenote_integration import save_to_onenote, test_onenote_connection

def main():
    print("YouTube Video Summarizer using LangChain + Gemini")
    print("=" * 50)
    
    # Check if GOOGLE_API_KEY is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Please set the GOOGLE_API_KEY environment variable")
        print("You can get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Check OneNote setup
    onenote_enabled = bool(os.getenv("MICROSOFT_CLIENT_ID"))
    if onenote_enabled:
        print("📓 OneNote integration: ENABLED")
        # Optionally test connection
        test_conn = input("Test OneNote connection? (y/n): ").strip().lower()
        if test_conn == 'y':
            success, message = test_onenote_connection()
            print(message)
            if not success:
                onenote_enabled = False
    else:
        print("📓 OneNote integration: DISABLED (add MICROSOFT_CLIENT_ID to .env to enable)")
    
    print()
    
    # Example YouTube URL (you can change this)
    url = input("Enter YouTube URL (or press Enter for demo): ").strip()
    if not url:
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll as demo
        print(f"Using demo URL: {url}")
    
    print("\n🔄 Extracting transcript...")
    transcript, error = get_transcript(url)
    
    if error:
        print(f"Error: {error}")
        return
    
    if not transcript:
        print("❌ No transcript found")
        return
    
    print(f"✅ Transcript extracted ({len(transcript)} characters)")
    print("\n🤖 Generating summary with LangChain + Gemini...")
    
    try:
        summary = summarize_transcript(transcript)
        print("✅ Summary generated!")
        print("\n" + "="*50)
        print(summary)
        print("="*50)
        
        # Extract video title from URL or use a default
        video_title = "YouTube Video Summary"
        try:
            # You could enhance this by extracting actual video title using yt-dlp
            import yt_dlp
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'YouTube Video Summary')
        except:
            pass  # Use default title if extraction fails
        
        # Save options
        print("\n" + "="*50)
        print("💾 Save Options:")
        
        # Save to file option
        save_file = input("Save summary to markdown file? (y/n): ").strip().lower()
        if save_file == 'y':
            filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {video_title}\n\n")
                f.write(f"**URL:** {url}\n\n")
                f.write(summary)
            print(f"✅ Summary saved to {filename}")
        
        # Save to OneNote option
        if onenote_enabled:
            save_onenote = input("Save summary to OneNote? (y/n): ").strip().lower()
            if save_onenote == 'y':
                print("\n📓 Saving to OneNote...")
                success, message, page_url = save_to_onenote(video_title, url, summary, transcript)
                print(message)
                
                if success and page_url:
                    open_page = input("Open OneNote page in browser? (y/n): ").strip().lower()
                    if open_page == 'y':
                        import webbrowser
                        webbrowser.open(page_url)
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

if __name__ == "__main__":
    main()
