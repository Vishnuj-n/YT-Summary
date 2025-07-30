import requests
import json
import re
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

class OneNoteManager:
    """Manages OneNote operations using Microsoft Graph API."""
    
    def __init__(self, access_token):
        """Initialize with Microsoft Graph access token."""
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_or_create_notebook(self, notebook_name="YouTube Summaries"):
        """Find existing notebook or create new one."""
        print(f"📓 Looking for notebook: {notebook_name}")
        
        # Get all notebooks
        response = requests.get(
            f"{self.base_url}/me/onenote/notebooks",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get notebooks: {response.text}")
        
        notebooks = response.json().get("value", [])
        
        # Look for existing notebook
        for notebook in notebooks:
            if notebook["displayName"] == notebook_name:
                print(f"✅ Found existing notebook: {notebook['id']}")
                return notebook["id"]
        
        # Create new notebook
        print(f"📝 Creating new notebook: {notebook_name}")
        create_data = {
            "displayName": notebook_name
        }
        
        response = requests.post(
            f"{self.base_url}/me/onenote/notebooks",
            headers=self.headers,
            json=create_data
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create notebook: {response.text}")
        
        notebook = response.json()
        print(f"✅ Created notebook: {notebook['id']}")
        return notebook["id"]
    
    def get_or_create_section(self, notebook_id, section_name="AI Generated Summaries"):
        """Find existing section or create new one."""
        print(f"📂 Looking for section: {section_name}")
        
        # Get all sections in notebook
        response = requests.get(
            f"{self.base_url}/me/onenote/notebooks/{notebook_id}/sections",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get sections: {response.text}")
        
        sections = response.json().get("value", [])
        
        # Look for existing section
        for section in sections:
            if section["displayName"] == section_name:
                print(f"✅ Found existing section: {section['id']}")
                return section["id"]
        
        # Create new section
        print(f"📝 Creating new section: {section_name}")
        create_data = {
            "displayName": section_name
        }
        
        response = requests.post(
            f"{self.base_url}/me/onenote/notebooks/{notebook_id}/sections",
            headers=self.headers,
            json=create_data
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create section: {response.text}")
        
        section = response.json()
        print(f"✅ Created section: {section['id']}")
        return section["id"]
    
    def create_summary_page(self, section_id, video_title, video_url, summary, transcript_preview=None):
        """Create a new page with the video summary."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        page_title = f"{video_title} - {datetime.now().strftime('%Y-%m-%d')}"
        
        print(f"📄 Creating page: {page_title}")
        
        # Format the summary content
        html_content = self.format_summary_html(
            video_title, video_url, summary, timestamp, transcript_preview
        )
        
        # Create page headers for OneNote API
        page_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "text/html"
        }
        
        # Create the page
        response = requests.post(
            f"{self.base_url}/me/onenote/sections/{section_id}/pages",
            headers=page_headers,
            data=html_content.encode('utf-8')
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create page: {response.text}")
        
        page = response.json()
        page_url = page.get("links", {}).get("oneNoteWebUrl", {}).get("href", "")
        
        print(f"✅ Page created successfully!")
        if page_url:
            print(f"🔗 View at: {page_url}")
        
        return page["id"], page_url
    
    def format_summary_html(self, video_title, video_url, summary, timestamp, transcript_preview=None):
        """Convert markdown summary to OneNote HTML format."""
        
        # Start with OneNote HTML template
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{self._escape_html(video_title)}</title>
    <meta name="created" content="{timestamp}" />
</head>
<body>
    <div>
        <h1 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 8px;">
            🎥 {self._escape_html(video_title)}
        </h1>
        
        <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px; margin: 16px 0;">
            <p><strong>📺 Video URL:</strong> <a href="{video_url}" target="_blank">{video_url}</a></p>
            <p><strong>📅 Generated:</strong> {timestamp}</p>
            <p><strong>🤖 AI Model:</strong> Google Gemini via LangChain</p>
        </div>
"""
        
        # Add transcript preview if available
        if transcript_preview:
            html_content += f"""
        <h2 style="color: #059669; margin-top: 24px;">📝 Transcript Preview</h2>
        <div style="background-color: #f0f9ff; padding: 12px; border-left: 4px solid #0284c7; margin: 12px 0; font-style: italic;">
            {self._escape_html(transcript_preview[:500])}{"..." if len(transcript_preview) > 500 else ""}
        </div>
"""
        
        # Convert markdown summary to HTML
        summary_html = self._markdown_to_html(summary)
        html_content += f"""
        <h2 style="color: #dc2626; margin-top: 24px;">🤖 AI Generated Summary</h2>
        <div style="line-height: 1.6;">
            {summary_html}
        </div>
        
        <div style="margin-top: 32px; padding: 16px; background-color: #fef3c7; border-radius: 8px;">
            <h3 style="color: #92400e; margin-top: 0;">🔗 Quick Actions</h3>
            <p>
                <a href="{video_url}" target="_blank" style="color: #dc2626; text-decoration: none; font-weight: bold;">▶️ Watch Video</a> | 
                <a href="{video_url}&t=0s" target="_blank" style="color: #dc2626; text-decoration: none;">⏰ Start from Beginning</a>
            </p>
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
    def _markdown_to_html(self, markdown_text):
        """Convert markdown to HTML for OneNote."""
        html = markdown_text
        
        # Convert headers
        html = re.sub(r'^### (.*$)', r'<h3 style="color: #7c3aed;">\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*$)', r'<h2 style="color: #059669;">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*$)', r'<h1 style="color: #dc2626;">\1</h1>', html, flags=re.MULTILINE)
        
        # Convert bullet points
        html = re.sub(r'^\* (.*$)', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        html = re.sub(r'</ul>\s*<ul>', '', html)
        
        # Convert bold text
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Convert paragraphs
        paragraphs = html.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                para = f'<p>{para}</p>'
            formatted_paragraphs.append(para)
        
        return '\n'.join(formatted_paragraphs)
    
    def _escape_html(self, text):
        """Escape HTML special characters."""
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def list_recent_pages(self, section_id, count=10):
        """List recent pages in the section."""
        response = requests.get(
            f"{self.base_url}/me/onenote/sections/{section_id}/pages?$top={count}&$orderby=createdDateTime desc",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get pages: {response.text}")
        
        pages = response.json().get("value", [])
        return [(page["title"], page.get("links", {}).get("oneNoteWebUrl", {}).get("href", "")) for page in pages]
    
    def search_pages(self, query, notebook_id=None):
        """Search for pages containing the query."""
        search_url = f"{self.base_url}/me/onenote/pages"
        
        if notebook_id:
            search_url += f"?$filter=parentNotebook/id eq '{notebook_id}'"
        
        # Add search query
        search_params = f"&$search={quote(query)}" if '?' in search_url else f"?$search={quote(query)}"
        search_url += search_params
        
        response = requests.get(search_url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to search pages: {response.text}")
        
        pages = response.json().get("value", [])
        return [(page["title"], page.get("links", {}).get("oneNoteWebUrl", {}).get("href", "")) for page in pages]
