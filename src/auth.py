"""
Google Workspace OAuth 2.0 Authentication Module
Handles authentication for all Google Workspace services
"""

import os
import json
import pickle
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class GoogleAuthenticator:
    """Manages OAuth 2.0 authentication for Google Workspace APIs"""

    # Define scopes for all Google Workspace services
    SCOPES = [
        # Gmail
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.compose',

        # Google Chat
        'https://www.googleapis.com/auth/chat.spaces',
        'https://www.googleapis.com/auth/chat.messages',

        # Google Sheets
        'https://www.googleapis.com/auth/spreadsheets',

        # Google Drive
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',

        # Google Forms
        'https://www.googleapis.com/auth/forms.body',
        'https://www.googleapis.com/auth/forms.responses.readonly',

        # Google Calendar
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events',

        # Google Docs
        'https://www.googleapis.com/auth/documents',
    ]

    def __init__(self, credentials_dir: str = '/data/credentials'):
        """
        Initialize the authenticator

        Args:
            credentials_dir: Directory containing credentials and tokens
        """
        self.credentials_dir = Path(credentials_dir)
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

        self.credentials_file = self.credentials_dir / 'client_secret.json'
        self.token_file = self.credentials_dir / 'token.pickle'

    def get_credentials(self) -> Optional[Credentials]:
        """
        Get or refresh OAuth credentials

        Returns:
            Valid credentials or None if authentication is needed
        """
        creds = None

        # Load existing token if available
        if self.token_file.exists():
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or obtain new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Failed to refresh token: {e}")
                    creds = None

            if not creds:
                # Check if credentials file exists
                if not self.credentials_file.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_file}. "
                        "Please provide a valid OAuth 2.0 client secret JSON file."
                    )

                # Perform OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file),
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def is_authenticated(self) -> bool:
        """Check if valid credentials exist"""
        try:
            creds = self.get_credentials()
            return creds is not None and creds.valid
        except Exception:
            return False

    def revoke_credentials(self) -> None:
        """Revoke and remove stored credentials"""
        if self.token_file.exists():
            self.token_file.unlink()
