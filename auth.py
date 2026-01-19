import json
import time
import requests
import webbrowser
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from typing import Optional, Dict, Any

from config import Settings
from exceptions import FitbitAuthError

logger = logging.getLogger(__name__)

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        if "code" in params:
            self.server.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization successful!</h1><p>You can close this window now.</p>")
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default server logging
        pass

class FitbitAuth:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.auth_url = "https://www.fitbit.com/oauth2/authorize"
        self.token_url = "https://api.fitbit.com/oauth2/token"
        self.scope = "activity profile"

    def get_token(self) -> str:
        if self.settings.token_file.exists():
            try:
                with open(self.settings.token_file, "r") as f:
                    token_data = json.load(f)
                    if token_data.get("expires_at", 0) > time.time():
                        return token_data["access_token"]
                    else:
                        logger.info("Token expired, refreshing...")
                        return self.refresh_token(token_data)
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error reading token file: {e}")
                pass # Fallback to authorization
        
        return self.authorize()

    def authorize(self) -> str:
        # Start local server to listen for callback
        server = HTTPServer(('localhost', 8080), OAuthHandler)
        server.auth_code = None
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=server.handle_request)
        server_thread.start()

        # Construct auth URL
        url = (f"{self.auth_url}?response_type=code&client_id={self.settings.client_id}"
               f"&redirect_uri={self.settings.redirect_uri}&scope={self.scope}&expires_in=604800")
        
        logger.info(f"Opening browser for authorization: {url}")
        webbrowser.open(url)
        
        server_thread.join() # Wait for request to be handled
        
        if server.auth_code:
            return self.exchange_code_for_token(server.auth_code)
        else:
            raise FitbitAuthError("Authorization failed or timed out.")

    def exchange_code_for_token(self, code: str) -> str:
        data = {
            "client_id": self.settings.client_id,
            "grant_type": "authorization_code",
            "redirect_uri": self.settings.redirect_uri,
            "code": code
        }
        auth_header = requests.auth.HTTPBasicAuth(self.settings.client_id, self.settings.client_secret)
        
        try:
            response = requests.post(self.token_url, data=data, auth=auth_header)
            response.raise_for_status()
            return self.save_token(response.json())
        except requests.RequestException as e:
            logger.error(f"Failed to exchange code: {e}")
            if response is not None:
                logger.error(f"Response: {response.text}")
            raise FitbitAuthError(f"Failed to exchange code: {e}")

    def refresh_token(self, token_data: Dict[str, Any]) -> str:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": token_data["refresh_token"]
        }
        auth_header = requests.auth.HTTPBasicAuth(self.settings.client_id, self.settings.client_secret)
        
        try:
            response = requests.post(self.token_url, data=data, auth=auth_header)
            
            if response.status_code != 200:
                logger.warning(f"Failed to refresh token: {response.text}")
                return self.authorize()

            return self.save_token(response.json())
        except requests.RequestException as e:
            logger.error(f"Error during token refresh: {e}")
            return self.authorize()

    def save_token(self, token_response: Dict[str, Any]) -> str:
        # Calculate expiry time
        token_response["expires_at"] = time.time() + token_response["expires_in"]
        
        with open(self.settings.token_file, "w") as f:
            json.dump(token_response, f)
        
        logger.info("Token saved successfully.")
        return token_response["access_token"]
