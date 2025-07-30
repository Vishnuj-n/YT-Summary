# OneNote Integration Setup Guide

## 🎯 Overview
This guide will help you set up Microsoft OneNote integration to automatically save your YouTube video summaries as OneNote pages.

## 📋 Prerequisites
- Microsoft account with OneNote access
- Azure account (free tier is sufficient)
- Your existing YouTube summarizer project

## 🔧 Step-by-Step Setup

### Step 1: Create Azure App Registration

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to App Registrations**:
   - Search for "App registrations" in the top search bar
   - Click on "App registrations"

3. **Create New Registration**:
   - Click "New registration"
   - Fill in the details:
     - **Name**: `YouTube Summarizer OneNote`
     - **Supported account types**: `Personal Microsoft accounts only`
     - **Redirect URI**: 
       - Platform: `Web`
       - URI: `http://localhost:8765/callback`
   - Click "Register"

### Step 2: Get Application Credentials

1. **Copy Application (client) ID**:
   - On the app overview page, copy the "Application (client) ID"
   - This will be your `MICROSOFT_CLIENT_ID`

2. **Create Client Secret**:
   - Go to "Certificates & secrets" in the left menu
   - Click "New client secret"
   - Description: `OneNote Access`
   - Expires: `24 months` (or your preference)
   - Click "Add"
   - **Copy the secret VALUE immediately** (it won't be shown again)
   - This will be your `MICROSOFT_CLIENT_SECRET`

### Step 3: Configure API Permissions

1. **Go to API Permissions**:
   - Click "API permissions" in the left menu
   - Click "Add a permission"

2. **Add Microsoft Graph Permissions**:
   - Click "Microsoft Graph"
   - Click "Delegated permissions"
   - Search for and select:
     - `Notes.Create`
     - `Notes.ReadWrite`
   - Click "Add permissions"

3. **Grant Admin Consent** (if required):
   - Click "Grant admin consent for [your organization]"
   - Click "Yes"

### Step 4: Update Environment Variables

1. **Edit your `.env` file**:
   ```bash
   # Google API (existing)
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Microsoft Graph API (new)
   MICROSOFT_CLIENT_ID=your_copied_client_id_here
   MICROSOFT_CLIENT_SECRET=your_copied_client_secret_here
   
   # OneNote Configuration (optional customization)
   ONENOTE_NOTEBOOK_NAME=YouTube Summaries
   ONENOTE_SECTION_NAME=AI Generated Summaries
   ```

### Step 5: Install Dependencies

```bash
# Install the new dependencies
uv sync
```

### Step 6: Test the Setup

1. **Run the test**:
   ```bash
   python -c "from onenote_integration import test_onenote_connection; print(test_onenote_connection())"
   ```

2. **First-time authentication**:
   - The system will open your browser
   - Log in with your Microsoft account
   - Grant permissions to the app
   - You should see "Authentication successful!"

## 🚀 Usage

### Basic Usage
```bash
python main.py
```

The script will now ask if you want to save to OneNote after generating a summary.

### Programmatic Usage
```python
from onenote_integration import save_to_onenote

# After generating your summary
success, message, page_url = save_to_onenote(
    video_title="My Video Title",
    video_url="https://youtube.com/watch?v=...",
    summary="Generated summary content...",
    transcript="Original transcript..."  # optional
)

if success:
    print(f"Saved! View at: {page_url}")
else:
    print(f"Error: {message}")
```

## 📓 What Gets Created in OneNote

### Notebook Structure
```
YouTube Summaries (Notebook)
└── AI Generated Summaries (Section)
    ├── Video Title 1 - 2025-01-15 (Page)
    ├── Video Title 2 - 2025-01-15 (Page)
    └── ...
```

### Page Content
Each page includes:
- 🎥 **Video title and metadata**
- 📺 **Direct link to YouTube video**
- 📅 **Generation timestamp**
- 📝 **Transcript preview** (first 500 characters)
- 🤖 **Full AI-generated summary** with proper formatting
- 🔗 **Quick action links**

## 🔧 Troubleshooting

### Common Issues

1. **"Authentication failed"**:
   - Check your client ID and secret in `.env`
   - Ensure redirect URI is exactly: `http://localhost:8765/callback`
   - Try clearing token cache: delete `token_cache.json`

2. **"Permission denied"**:
   - Verify API permissions are granted
   - Ensure you granted admin consent
   - Check if your Microsoft account has OneNote access

3. **"Notebook creation failed"**:
   - Make sure you have OneNote in your Microsoft account
   - Try accessing OneNote web at https://onenote.com first

4. **"Import errors"**:
   - Run `uv sync` to install missing packages
   - Check that all new files are in your project directory

### Reset Authentication
```bash
# Clear stored tokens
python -c "from auth_manager import AuthManager; AuthManager('dummy').clear_cache()"
```

## 🎨 Customization

### Change Notebook/Section Names
Edit your `.env` file:
```bash
ONENOTE_NOTEBOOK_NAME=My Custom Notebook
ONENOTE_SECTION_NAME=My Custom Section
```

### Modify Page Template
Edit the `format_summary_html()` method in `onenote_manager.py` to customize:
- Colors and styling
- Content layout
- Additional metadata
- Custom sections

## 🔒 Security Notes

- **Client secrets**: Keep your `MICROSOFT_CLIENT_SECRET` secure
- **Token storage**: Tokens are cached locally in `token_cache.json`
- **Permissions**: The app only requests minimum required OneNote permissions
- **Data**: No data is sent to third parties - direct connection to Microsoft Graph API

## 📈 Advanced Features

### Search Summaries
```python
from onenote_integration import search_summaries

success, results, message = search_summaries("machine learning")
for title, url in results:
    print(f"{title}: {url}")
```

### List Recent Summaries
```python
from onenote_integration import list_recent_summaries

success, summaries, message = list_recent_summaries(count=10)
for title, url in summaries:
    print(f"{title}: {url}")
```

## 🎉 Success!

Once set up, every YouTube video summary will be automatically saved to OneNote, accessible across all your devices with rich formatting and easy searchability!
