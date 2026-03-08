"""Unit tests for BaseAnalyzer abstract class."""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from analyzers.base_analyzer import BaseAnalyzer


class ConcreteAnalyzer(BaseAnalyzer):
    """Concrete implementation of BaseAnalyzer for testing."""

    def __init__(self, *args, **kwargs):
        """Initialize concrete analyzer."""
        super().__init__('TestAnalyzer', *args, **kwargs)

    def search_emails(self):
        """Search emails - returns test data."""
        return [
            {
                'id': 'msg1',
                'payload': {'headers': [{'name': 'From', 'value': 'test@example.com'}]}
            }
        ]

    def parse_documents(self, emails):
        """Parse documents - returns test data."""
        return [
            {
                'provider': 'TestProvider',
                'account_id': '123456',
                'amount_due': 100.00,
                'bill_date': '2025-02-28'
            }
        ]


class TestBaseAnalyzerInitialization:
    """Test BaseAnalyzer initialization."""

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters."""
        analyzer = ConcreteAnalyzer()
        assert analyzer.analyzer_name == 'TestAnalyzer'
        assert analyzer.config == {}
        assert analyzer.service is None

    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = {'max_results': 50}
        analyzer = ConcreteAnalyzer(config=config)
        assert analyzer.config == config

    def test_initialization_with_custom_credentials_paths(self):
        """Test initialization with custom credential file paths."""
        analyzer = ConcreteAnalyzer(
            credentials_file='custom_creds.json',
            token_file='custom_token.json'
        )
        assert analyzer.auth_manager.credentials_file == 'custom_creds.json'
        assert analyzer.auth_manager.token_file == 'custom_token.json'


class TestSearchEmailsGeneric:
    """Test generic email search functionality."""

    def test_search_emails_generic_success(self, mock_gmail_service):
        """Test successful email search."""
        analyzer = ConcreteAnalyzer(credentials_file='fake.json', token_file='fake.json')
        analyzer.service = mock_gmail_service

        # Mock Gmail API response
        mock_gmail_service.users().messages().list().execute.return_value = {
            'messages': [
                {'id': 'msg1'},
                {'id': 'msg2'},
            ]
        }

        mock_gmail_service.users().messages().get().execute.side_effect = [
            {'id': 'msg1', 'payload': {}},
            {'id': 'msg2', 'payload': {}},
        ]

        emails = analyzer.search_emails_generic('from:test@example.com', max_results=10)

        assert len(emails) == 2
        assert emails[0]['id'] == 'msg1'
        assert emails[1]['id'] == 'msg2'

    def test_search_emails_generic_no_results(self, mock_gmail_service):
        """Test email search with no results."""
        analyzer = ConcreteAnalyzer(credentials_file='fake.json', token_file='fake.json')
        analyzer.service = mock_gmail_service

        mock_gmail_service.users().messages().list().execute.return_value = {
            'messages': []
        }

        emails = analyzer.search_emails_generic('from:nonexistent@example.com')

        assert emails == []

    def test_search_emails_generic_api_error(self, mock_gmail_service):
        """Test email search with API error."""
        analyzer = ConcreteAnalyzer(credentials_file='fake.json', token_file='fake.json')
        analyzer.service = mock_gmail_service

        mock_gmail_service.users().messages().list().execute.side_effect = Exception('API Error')

        emails = analyzer.search_emails_generic('from:test@example.com')

        assert emails == []


class TestExportJson:
    """Test JSON export functionality."""

    def test_export_json_success(self):
        """Test successful JSON export."""
        analyzer = ConcreteAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test_data.json')
            data = [
                {'id': 1, 'name': 'Test 1'},
                {'id': 2, 'name': 'Test 2'},
            ]

            result = analyzer.export_json(data, filepath)

            assert result == filepath
            assert os.path.exists(filepath)

            # Verify file contents
            with open(filepath, 'r') as f:
                saved_data = json.load(f)
            assert saved_data == data

    def test_export_json_creates_directory(self):
        """Test that export_json creates directories if needed."""
        analyzer = ConcreteAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'subdir', 'another', 'test_data.json')
            data = [{'id': 1}]

            result = analyzer.export_json(data, filepath)

            assert os.path.exists(filepath)
            with open(filepath, 'r') as f:
                saved_data = json.load(f)
            assert saved_data == data

    def test_export_json_invalid_path(self):
        """Test export with invalid path raises error."""
        analyzer = ConcreteAnalyzer()
        data = [{'id': 1}]

        with pytest.raises(IOError):
            analyzer.export_json(data, '/invalid/nonexistent/path/file.json')


class TestRun:
    """Test full analysis pipeline."""

    def test_run_success(self):
        """Test successful complete run."""
        analyzer = ConcreteAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp dir for export
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            os.makedirs('data', exist_ok=True)

            try:
                data, json_file, html_file = analyzer.run()

                assert len(data) == 1
                assert data[0]['provider'] == 'TestProvider'
                assert os.path.exists(json_file)
                assert json_file.endswith('_data.json')

                # Verify exported data
                with open(json_file, 'r') as f:
                    saved_data = json.load(f)
                assert saved_data == data

            finally:
                os.chdir(original_cwd)

    def test_run_with_no_emails(self):
        """Test run when no emails are found."""
        class NoEmailAnalyzer(BaseAnalyzer):
            def search_emails(self):
                return []

            def parse_documents(self, emails):
                return []

        analyzer = NoEmailAnalyzer('NoEmailAnalyzer')
        data, json_file, html_file = analyzer.run()

        assert data == []
        assert json_file == ''
        assert html_file == ''


class TestGetMetadata:
    """Test metadata method."""

    def test_get_metadata(self):
        """Test get_metadata returns expected structure."""
        analyzer = ConcreteAnalyzer()
        metadata = analyzer.get_metadata()

        assert 'name' in metadata
        assert 'version' in metadata
        assert 'supported_providers' in metadata
        assert 'output_schema' in metadata
        assert metadata['name'] == 'TestAnalyzer'
