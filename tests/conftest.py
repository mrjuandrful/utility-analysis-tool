"""Pytest configuration and shared fixtures."""

import json
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime


@pytest.fixture
def mock_gmail_service():
    """Mock Gmail API service for testing."""
    service = MagicMock()
    return service


@pytest.fixture
def sample_utility_email():
    """Sample PSEG utility bill email."""
    return {
        'id': 'msg_utility_1',
        'threadId': 'thread_1',
        'labelIds': ['INBOX'],
        'snippet': 'Your PSEG bill is ready',
        'internalDate': '1740720000000',  # 2025-02-28
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'billing@pseg.com'},
                {'name': 'Subject', 'value': 'Your PSEG Bill is Ready'},
                {'name': 'Date', 'value': 'Fri, 28 Feb 2025 10:00:00 -0700'},
            ],
            'mimeType': 'text/html',
            'body': {
                'data': 'QmlsbCBBbW91bnQ6IDEwMTIzLjQzCkFjY291bnQ6IFhYWFgwOTA2CkR1ZSBEYXRlOiBNYXIgMTUsIDIwMjU='  # Base64 encoded
            }
        }
    }


@pytest.fixture
def sample_telecom_email():
    """Sample Verizon Fios email."""
    return {
        'id': 'msg_telecom_1',
        'threadId': 'thread_2',
        'labelIds': ['INBOX'],
        'snippet': 'Your Verizon Fios bill is ready',
        'internalDate': '1740720000000',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'verizon-notification@ecrm-mail.verizon.com'},
                {'name': 'Subject', 'value': 'Your Verizon Fios Bill is Ready'},
                {'name': 'Date', 'value': 'Fri, 28 Feb 2025 10:00:00 -0700'},
            ],
            'mimeType': 'text/html',
            'body': {
                'data': 'QmlsbCBBbW91bnQ6IDEwMTIzLjk5CkFjY291bnQ6IDg2Ny0wMDAxCg=='
            }
        }
    }


@pytest.fixture
def sample_amex_email():
    """Sample AMEX credit card statement email."""
    return {
        'id': 'msg_amex_1',
        'threadId': 'thread_3',
        'labelIds': ['INBOX'],
        'snippet': 'Your AMEX statement is ready',
        'internalDate': '1740720000000',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'noreply@americanexpress.com'},
                {'name': 'Subject', 'value': 'Your February 2026 Statement'},
                {'name': 'Date', 'value': 'Fri, 28 Feb 2025 10:00:00 -0700'},
            ],
            'mimeType': 'text/html',
            'body': {
                'data': 'PGh0bWw+PHRhYmxlPjx0cj48dGQ+MDIvMDMvMjAyNjwvdGQ+PHRkPkFNQVpPTi5DT00gU0VBVFRMRTwvdGQ+PHRkPjQ1Ljk5PC90ZD48L3RyPjwvdGFibGU+PC9odG1sPg=='
            }
        }
    }


@pytest.fixture
def expected_utility_output():
    """Expected output from utility analyzer."""
    return {
        'provider': 'PSEG',
        'account_id': 'XXXX0906',
        'bills': [
            {
                'bill_date': '2025-02-28',
                'amount_due': 156.43,
                'email_date': '2025-02-28T10:00:00-07:00'
            }
        ]
    }


@pytest.fixture
def expected_telecom_output():
    """Expected output from telecom analyzer."""
    return {
        'carriers': [
            {
                'carrier': 'Verizon Fios',
                'account_id': '867-0001',
                'service_type': 'home_internet_phone',
                'bills': [
                    {
                        'bill_date': '2025-02-28',
                        'amount_due': 42.99,
                        'email_date': '2025-02-28T10:00:00-07:00'
                    }
                ]
            }
        ]
    }


@pytest.fixture
def expected_amex_output():
    """Expected output from AMEX analyzer."""
    return {
        'issuer': 'American Express',
        'account_last_four': '63007',
        'statements': [
            {
                'statement_date': '2026-02-15',
                'transactions': [
                    {
                        'date': '2026-02-03',
                        'description': 'AMAZON.COM SEATTLE WA',
                        'amount': 45.99,
                        'category': 'Shopping'
                    }
                ]
            }
        ]
    }
