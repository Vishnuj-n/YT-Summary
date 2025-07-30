import os
import msal
import webbrowser
import json
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

class CallbackHandler(BaseHTTPRequestHandler):
    """Handle the OAuth callback from Microsoft."""
    
    def do_GET(self):
        """Handle GET request with authorization code."""
        self.server.auth_code = None
        self.server.error = None
        
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' in query_params:
            self.server.auth_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
            <html><body>
            <h2>Authentication Successful!</h2>
            <p>You can close this window and return to your application.</p>
            </body></html>
            """)
        elif 'error' in query_params:
            self.server.error = query_params['error'][0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h2>Error: {self.server.error}</h2></body></html>".encode())
        
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass

class AuthManager:
    """Manages Microsoft Graph authentication using MSAL."""
    
    def __init__(self, client_id, client_secret=None):
        """Initialize MSAL for Microsoft authentication."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = "http://localhost:8765/callback"
        self.authority = "https://login.microsoftonline.com/common"
        self.scopes = ["https://graph.microsoft.com/Notes.Create", 
                      "https://graph.microsoft.com/Notes.ReadWrite"]
        
        # Token cache file
        self.token_cache_file = "token_cache.json"
        
        # Initialize MSAL app
        cache = self._load_token_cache()
        if client_secret:
            self.app = msal.ConfidentialClientApplication(
                client_id=client_id,
                client_credential=client_secret,
                authority=self.authority,
                token_cache=cache
            )
        else:
            self.app = msal.PublicClientApplication(
                client_id=client_id,
                authority=self.authority,
                token_cache=cache
            )
    
    def _load_token_cache(self):
        """Load token cache from file."""
        cache = msal.SerializableTokenCache()
        if os.path.exists(self.token_cache_file):
            try:
                with open(self.token_cache_file, 'r') as f:
                    cache.deserialize(f.read())
            except Exception as e:
                print(f"Warning: Could not load token cache: {e}")
        return cache
    
    def _save_token_cache(self):
        """Save token cache to file."""
        if self.app.token_cache.has_state_changed:
            try:
                with open(self.token_cache_file, 'w') as f:
                    f.write(self.app.token_cache.serialize())
            except Exception as e:
                print(f"Warning: Could not save token cache: {e}")
    
    def get_access_token(self):
        """Get access token using the best available method."""
        # Try to get token silently first
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
            if result and "access_token" in result:
                self._save_token_cache()
                return result["access_token"]
        
        # If silent acquisition fails, use interactive flow
        if self.client_secret:
            return self._device_code_flow()
        else:
            return self._web_browser_flow()
    
    def _device_code_flow(self):
        """Use device code flow for authentication."""
        print("🔐 Starting device code authentication...")
        
        flow = self.app.initiate_device_flow(scopes=self.scopes)
        if "user_code" not in flow:
            raise Exception("Failed to create device flow")
        
        print(f"\n📱 Please visit: {flow['verification_uri']}")
        print(f"🔢 Enter code: {flow['user_code']}")
        print("⏳ Waiting for authentication...")
        
        result = self.app.acquire_token_by_device_flow(flow)
        
        if "access_token" in result:
            self._save_token_cache()
            print("✅ Authentication successful!")
            return result["access_token"]
        else:
            error = result.get("error_description", "Unknown error")
            raise Exception(f"Authentication failed: {error}")
    
    def _web_browser_flow(self):
        """Use web browser flow for authentication."""
        print("🔐 Starting web browser authentication...")
        
        # Start local server
        server = HTTPServer(('localhost', 8765), CallbackHandler)
        server.auth_code = None
        server.error = None
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        try:
            # Get authorization URL
            auth_url = self.app.get_authorization_request_url(
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            print("🌐 Opening browser for authentication...")
            webbrowser.open(auth_url)
            
            # Wait for callback
            timeout = 120  # 2 minutes
            start_time = time.time()
            
            while server.auth_code is None and server.error is None:
                if time.time() - start_time > timeout:
                    raise Exception("Authentication timeout")
                time.sleep(1)
            
            if server.error:
                raise Exception(f"Authentication error: {server.error}")
            
            if not server.auth_code:
                raise Exception("No authorization code received")
            
            # Exchange code for token
            result = self.app.acquire_token_by_authorization_code(
                server.auth_code,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            if "access_token" in result:
                self._save_token_cache()
                print("✅ Authentication successful!")
                return result["access_token"]
            else:
                error = result.get("error_description", "Unknown error")
                raise Exception(f"Token exchange failed: {error}")
        
        finally:
            server.shutdown()
            server.server_close()
    
    def refresh_token(self, refresh_token):
        """Refresh expired access token."""
        try:
            accounts = self.app.get_accounts()
            if accounts:
                result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
                if result and "access_token" in result:
                    self._save_token_cache()
                    return result["access_token"]
        except Exception as e:
            print(f"Token refresh failed: {e}")
        
        # If refresh fails, get new token
        return self.get_access_token()
    
    def clear_cache(self):
        """Clear stored token cache."""
        if os.path.exists(self.token_cache_file):
            os.remove(self.token_cache_file)
            print("🗑️ Token cache cleared")
