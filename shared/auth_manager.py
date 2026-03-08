"""Gmail OAuth 2.0 authentication manager.

Handles Google API authentication, token refresh, and credential management.
Extracted from gmail_utility_analyzer.py to be reused across all analyzers.
"""

import os
import json
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery


class AuthManager:
    """Manages Gmail API authentication and credential persistence."""

    # Gmail API read-only scope
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self,
                 credentials_file: str = 'credentials.json',
                 token_file: str = 'token.json'):
        """
        Initialize authentication manager.

        Args:
            credentials_file: Path to OAuth 2.0 credentials.json from Google Cloud Console
            token_file: Path to store/retrieve OAuth tokens for future use
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None

    def authenticate(self) -> googleapiclient.discovery.Resource:
        """
        Authenticate with Gmail API.

        Uses OAuth 2.0 flow:
        1. First run: Prompts user to grant permission (opens browser)
        2. Subsequent runs: Uses stored token (auto-refresh if expired)
        3. If token expires: Automatically refreshes

        Returns:
            Gmail API service resource

        Raises:
            FileNotFoundError: If credentials.json not found in working directory
            Exception: If authentication fails
        """
        creds = None

        # Step 1: Check for stored token
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_file,
                    self.SCOPES
                )
            except Exception as e:
                print(f"Error loading token file: {e}")
                creds = None

        # Step 2: If no valid credentials, get new ones or refresh
        if creds is None or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Token expired but can be refreshed
                try:
                    creds.refresh(Request())
                    print("✓ Token refreshed successfully")
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    creds = None

            if creds is None:
                # Need to get new credentials from credentials.json
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"credentials.json not found in {os.getcwd()}\n"
                        "Download it from: https://console.cloud.google.com/apis/credentials\n"
                        "1. Create OAuth 2.0 Client ID (Desktop app)\n"
                        "2. Download as JSON and save as 'credentials.json'"
                    )

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file,
                        self.SCOPES
                    )
                    # This opens browser for user to grant permission
                    creds = flow.run_local_server(port=0)
                    print("✓ Authentication successful")
                except Exception as e:
                    raise Exception(f"OAuth flow failed: {e}")

        # Step 3: Save credentials for future use (if it's a new token)
        if creds:
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Warning: Could not save token file: {e}")

        # Build and return Gmail API service
        self.service = googleapiclient.discovery.build(
            'gmail', 'v1',
            credentials=creds,
            cache_discovery=False
        )
        return self.service

    def get_service(self) -> googleapiclient.discovery.Resource:
        """
        Get Gmail API service (lazy initialization).

        If service not yet authenticated, calls authenticate().
        If service exists, returns cached instance.

        Returns:
            Gmail API service resource
        """
        if self.service is None:
            self.authenticate()
        return self.service

    def revoke_credentials(self) -> bool:
        """
        Revoke stored credentials and delete token file.

        This logs out the user and requires re-authentication next time.

        Returns:
            True if revocation successful, False otherwise
        """
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
                print(f"✓ Token revoked and {self.token_file} deleted")
                self.service = None
                return True
            return False
        except Exception as e:
            print(f"Error revoking credentials: {e}")
            return False
