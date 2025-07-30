# YouTube Video Summarizer with LangChain + Gemini

A Python application that extracts transcripts from YouTube videos and generates comprehensive summaries using LangChain and Google's Gemini AI model.

## Features

- Extract transcripts from YouTube videos (manual or auto-generated captions)
- Generate comprehensive summaries using Google's Gemini model via LangChain
- Export summaries as Markdown files
- Support for multiple subtitle languages (defaults to English)

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

### Programmatic Usage

```python
from summary import get_transcript, summarize_transcript

# Extract transcript
transcript, error = get_transcript("https://www.youtube.com/watch?v=VIDEO_ID")

if not error:
    # Generate summary
    summary = summarize_transcript(transcript)
    print(summary)
```

## Summary Format

The generated summary includes:

- **Summary**: Detailed yet concise overview (300-500 words)
- **Key Points**: Essential concepts as bullet points
- **Detailed Breakdown**: Content organized into logical sections
- **Questions & Answers**: 5 thoughtful Q&A pairs
- **Key Terminology**: Important terms and definitions

## Technologies Used

- **LangChain**: Framework for building applications with LLMs
- **Google Gemini**: Advanced AI model for text generation
- **yt-dlp**: YouTube video processing and transcript extraction
- **Python-dotenv**: Environment variable management

## Environment Variables

- `GOOGLE_API_KEY`: Your Google AI API key (required)

## Error Handling

The application handles various error scenarios:
- Missing or invalid YouTube URLs
- No available subtitles/captions
- API rate limits or failures
- Network connectivity issues

## License

This project is open source and available under the MIT License.