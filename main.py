import os
from summary import get_transcript, summarize_transcript, download_markdown

def main():
    print("YouTube Video Summarizer using LangChain + Gemini")
    print("=" * 50)
    
    # Check if GOOGLE_API_KEY is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Please set the GOOGLE_API_KEY environment variable")
        print("You can get your API key from: https://makersuite.google.com/app/apikey")
        return
    
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
        
        # Optionally save to file
        save = input("\nSave summary to file? (y/n): ").strip().lower()
        if save == 'y':
            with open("summary.md", "w", encoding="utf-8") as f:
                f.write(summary)
            print("✅ Summary saved to summary.md")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

if __name__ == "__main__":
    main()
