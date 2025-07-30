# YouTube Video Summarizer with LangChain + Gemini + OneNote

A Python application that extracts transcripts from YouTube videos and generates comprehensive summaries using LangChain and Google's Gemini AI model. **NEW**: Automatically save summaries to Microsoft OneNote!

## Features

- Extract transcripts from YouTube videos (manual or auto-generated captions)
- Generate comprehensive summaries using Google's Gemini model via LangChain
- **🆕 OneNote Integration**: Automatically save summaries as OneNote pages
- Export summaries as Markdown files
- Support for multiple subtitle languages (defaults to English)
- Cross-device access through OneNote synchronization

## Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Get Google API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the `.env.example` file to `.env` and add your API key:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` and replace `your_google_api_key_here` with your actual API key

3. **🆕 OneNote Integration Setup** (Optional):
   - Follow the detailed guide in [`ONENOTE_SETUP.md`](ONENOTE_SETUP.md)
   - Set up Azure App Registration
   - Add Microsoft credentials to `.env` file
   - Summaries will be automatically saved to OneNote with rich formatting

## Usage

### Command Line Interface

Run the main script:
```bash
python main.py
```

The script will:
1. Prompt you for a YouTube URL
2. Extract the transcript
3. Generate a comprehensive summary using LangChain + Gemini
4. Optionally save the summary to a markdown file
5. **🆕 Optionally save the summary to OneNote** (if configured)

### Programmatic Usage

```python
from summary import get_transcript, summarize_transcript
from onenote_integration import save_to_onenote  # New OneNote integration

# Extract transcript
transcript, error = get_transcript("https://www.youtube.com/watch?v=VIDEO_ID")

if not error:
    # Generate summary
    summary = summarize_transcript(transcript)
    print(summary)
    
    # Save to OneNote (if configured)
    success, message, page_url = save_to_onenote(
        "Video Title", 
        "https://www.youtube.com/watch?v=VIDEO_ID", 
        summary, 
        transcript
    )
    if success:
        print(f"Saved to OneNote: {page_url}")
```

## Summary Format

The generated summary includes:

- **Summary**: Detailed yet concise overview (300-500 words)
- **Key Points**: Essential concepts as bullet points
- **Detailed Breakdown**: Content organized into logical sections
- **Questions & Answers**: 5 thoughtful Q&A pairs
- **Key Terminology**: Important terms and definitions

## 🆕 OneNote Integration Features

When OneNote integration is enabled, each summary creates a beautifully formatted page with:

- 🎥 **Video metadata** (title, URL, generation timestamp)
- 📝 **Transcript preview** (first 500 characters)
- 🤖 **Full AI summary** with proper formatting and colors
- 🔗 **Quick action links** to watch the video
- 📱 **Cross-device synchronization** via OneNote

### OneNote Page Structure
```
YouTube Summaries (Notebook)
└── AI Generated Summaries (Section)
    ├── Video Title 1 - 2025-01-15 (Page)
    ├── Video Title 2 - 2025-01-15 (Page)
    └── ...
```

## Technologies Used

- **LangChain**: Framework for building applications with LLMs
- **Google Gemini**: Advanced AI model for text generation
- **yt-dlp**: YouTube video processing and transcript extraction
- **Python-dotenv**: Environment variable management
- **🆕 Microsoft Graph API**: OneNote integration
- **🆕 MSAL**: Microsoft authentication

## Environment Variables

- `GOOGLE_API_KEY`: Your Google AI API key (required)
- `MICROSOFT_CLIENT_ID`: Azure app client ID (optional, for OneNote)
- `MICROSOFT_CLIENT_SECRET`: Azure app client secret (optional, for OneNote)
- `ONENOTE_NOTEBOOK_NAME`: Custom notebook name (optional, defaults to "YouTube Summaries")
- `ONENOTE_SECTION_NAME`: Custom section name (optional, defaults to "AI Generated Summaries")

## Error Handling

The application handles various error scenarios:
- Missing or invalid YouTube URLs
- No available subtitles/captions
- API rate limits or failures
- Network connectivity issues
- **🆕 Microsoft authentication failures**
- **🆕 OneNote permission issues**

## Quick Setup Commands

```bash
# Basic setup
git clone <your-repo>
cd summary
uv sync
cp .env.example .env
# Edit .env with your Google API key

# With OneNote integration
# Follow ONENOTE_SETUP.md for detailed Azure setup
# Add Microsoft credentials to .env
python main.py  # Will prompt for OneNote setup

# Test OneNote connection
python -c "from onenote_integration import test_onenote_connection; print(test_onenote_connection())"
```

## File Structure

```
summary/
├── summary.py              # Core AI logic
├── main.py                 # CLI interface
├── onenote_integration.py  # 🆕 OneNote integration helpers
├── onenote_manager.py      # 🆕 OneNote API management
├── auth_manager.py         # 🆕 Microsoft authentication
├── ONENOTE_SETUP.md       # 🆕 OneNote setup guide
├── pyproject.toml          # Dependencies
├── .env                    # Environment variables
└── README.md               # This file
```

## License

This project is open source and available under the MIT License.