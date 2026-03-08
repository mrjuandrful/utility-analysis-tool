"""Unit tests for AuthManager."""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, MagicMock, patch

from shared.auth_manager import AuthManager


class TestAuthManagerInitialization:
    """Test AuthManager initialization."""

    def test_initialization_defaults(self):
        """Test initialization with default paths."""
        manager = AuthManager()
        assert manager.credentials_file == 'credentials.json'
        assert manager.token_file == 'token.json'
        assert manager.service is None

    def test_initialization_custom_paths(self):
        """Test initialization with custom file paths."""
        manager = AuthManager(
            credentials_file='my_creds.json',
            token_file='my_token.json'
        )
        assert manager.credentials_file == 'my_creds.json'
        assert manager.token_file == 'my_token.json'


class TestAuthManagerAuthenticate:
    """Test authentication methods."""

    @patch('shared.auth_manager.googleapiclient.discovery.build')
    @patch('shared.auth_manager.Credentials')
    def test_authenticate_with_stored_token(self, mock_creds, mock_build):
        """Test authentication with existing token file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            token_file = os.path.join(tmpdir, 'token.json')

            # Create fake token file
            token_data = {
                'token': 'access_token_value',
                'refresh_token': 'refresh_token_value',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'client_id': 'client_id',
                'client_secret': 'client_secret',
                'scopes': ['https://www.googleapis.com/auth/gmail.readonly']
            }
            with open(token_file, 'w') as f:
                json.dump(token_data, f)

            manager = AuthManager(token_file=token_file)

            # Mock Credentials.from_authorized_user_file to return a valid cred
            mock_cred_instance = MagicMock()
            mock_cred_instance.valid = True
            mock_creds.from_authorized_user_file.return_value = mock_cred_instance

            mock_service = MagicMock()
            mock_build.return_value = mock_service

            # Authenticate
            service = manager.authenticate()

            # Verify token was loaded
            mock_creds.from_authorized_user_file.assert_called_once()
            assert service is not None

    def test_authenticate_missing_credentials_file(self):
        """Test authentication fails when credentials.json is missing."""
        manager = AuthManager(
            credentials_file='/nonexistent/credentials.json',
            token_file='/tmp/token.json'
        )

        with pytest.raises(FileNotFoundError) as exc_info:
            manager.authenticate()

        assert 'credentials.json not found' in str(exc_info.value)

    @patch('shared.auth_manager.googleapiclient.discovery.build')
    @patch('shared.auth_manager.Credentials')
    @patch('shared.auth_manager.InstalledAppFlow')
    def test_authenticate_new_credentials(self, mock_flow, mock_creds, mock_build):
        """Test authentication with new credentials from credentials.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = os.path.join(tmpdir, 'credentials.json')
            token_file = os.path.join(tmpdir, 'token.json')

            # Create fake credentials file
            creds_data = {'client_id': 'test_id', 'client_secret': 'test_secret'}
            with open(creds_file, 'w') as f:
                json.dump(creds_data, f)

            manager = AuthManager(
                credentials_file=creds_file,
                token_file=token_file
            )

            # Mock the flow
            mock_flow_instance = MagicMock()
            mock_cred_instance = MagicMock()
            mock_cred_instance.to_json.return_value = json.dumps(creds_data)
            mock_flow_instance.run_local_server.return_value = mock_cred_instance
            mock_flow.from_client_secrets_file.return_value = mock_flow_instance

            mock_service = MagicMock()
            mock_build.return_value = mock_service

            # Authenticate
            service = manager.authenticate()

            # Verify OAuth flow was initiated
            assert mock_flow.from_client_secrets_file.called
            assert os.path.exists(token_file)
            assert service is not None


class TestAuthManagerRevokeCredentials:
    """Test credential revocation."""

    def test_revoke_credentials_success(self):
        """Test successful credential revocation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            token_file = os.path.join(tmpdir, 'token.json')

            # Create fake token file
            with open(token_file, 'w') as f:
                json.dump({'token': 'test'}, f)

            manager = AuthManager(token_file=token_file)
            assert os.path.exists(token_file)

            # Revoke
            result = manager.revoke_credentials()

            assert result is True
            assert not os.path.exists(token_file)

    def test_revoke_credentials_no_token_file(self):
        """Test revoking when no token file exists."""
        manager = AuthManager(token_file='/nonexistent/token.json')
        result = manager.revoke_credentials()
        assert result is False


class TestGetService:
    """Test lazy service initialization."""

    @patch('shared.auth_manager.googleapiclient.discovery.build')
    @patch('shared.auth_manager.Credentials')
    def test_get_service_lazy_initialization(self, mock_creds, mock_build):
        """Test get_service initializes service on first call."""
        with tempfile.TemporaryDirectory() as tmpdir:
            token_file = os.path.join(tmpdir, 'token.json')

            # Create fake token
            with open(token_file, 'w') as f:
                json.dump({'token': 'test'}, f)

            manager = AuthManager(token_file=token_file)
            assert manager.service is None

            # Mock credentials
            mock_cred_instance = MagicMock()
            mock_cred_instance.valid = True
            mock_creds.from_authorized_user_file.return_value = mock_cred_instance

            mock_service = MagicMock()
            mock_build.return_value = mock_service

            # First call should initialize
            service1 = manager.get_service()
            assert service1 is not None

            # Second call should return same instance
            service2 = manager.get_service()
            assert service1 is service2
