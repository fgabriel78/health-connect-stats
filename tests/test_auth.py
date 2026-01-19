import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import time
from pathlib import Path
from auth import FitbitAuth
from config import Settings

class TestFitbitAuth(unittest.TestCase):
    def setUp(self):
        self.settings = Settings(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://localhost",
            token_file=Path("test_token.json")
        )
        self.auth = FitbitAuth(self.settings)

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_token_valid(self, mock_file, mock_exists):
        # Setup: Token file exists and is valid
        mock_exists.return_value = True
        token_data = {
            "access_token": "valid_token",
            "expires_at": time.time() + 3600
        }
        mock_file.return_value.read.return_value = json.dumps(token_data)
        
        token = self.auth.get_token()
        
        self.assertEqual(token, "valid_token")

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch('auth.FitbitAuth.refresh_token')
    def test_get_token_expired(self, mock_refresh, mock_file, mock_exists):
        # Setup: Token file exists but expired
        mock_exists.return_value = True
        token_data = {
            "access_token": "expired_token",
            "refresh_token": "ref_token",
            "expires_at": time.time() - 3600
        }
        mock_file.return_value.read.return_value = json.dumps(token_data)
        mock_refresh.return_value = "new_token"
        
        token = self.auth.get_token()
        
        self.assertEqual(token, "new_token")
        mock_refresh.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch('auth.FitbitAuth.authorize')
    def test_get_token_no_file(self, mock_authorize, mock_exists):
        # Setup: Token file does not exist
        mock_exists.return_value = False
        mock_authorize.return_value = "auth_token"
        
        token = self.auth.get_token()
        
        self.assertEqual(token, "auth_token")
        mock_authorize.assert_called_once()

if __name__ == '__main__':
    unittest.main()
