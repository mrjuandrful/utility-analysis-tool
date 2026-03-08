"""Abstract base class for financial document analyzers.

All domain-specific analyzers (Utility, Telecom, CreditCard) inherit from this
to ensure consistent interface, shared authentication, and common functionality.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import googleapiclient.discovery

from shared.auth_manager import AuthManager


class BaseAnalyzer(ABC):
    """
    Abstract base class for financial document analyzers.

    Subclasses must implement:
    - search_emails(): Domain-specific search query and email retrieval
    - parse_documents(): Domain-specific parsing of extracted data

    Shared functionality:
    - authenticate(): OAuth 2.0 authentication with Gmail API
    - search_emails_generic(): Generic email search implementation
    - export_json(): Standard JSON export format
    - generate_html_report(): Template-based HTML report generation (future)
    """

    def __init__(self,
                 analyzer_name: str,
                 config: Optional[Dict] = None,
                 credentials_file: str = 'credentials.json',
                 token_file: str = 'token.json'):
        """
        Initialize analyzer.

        Args:
            analyzer_name: Name of analyzer (e.g., 'UtilityAnalyzer', 'TelecomAnalyzer')
            config: Configuration dict with analyzer-specific settings
            credentials_file: Path to OAuth credentials.json
            token_file: Path to store/retrieve OAuth tokens
        """
        self.analyzer_name = analyzer_name
        self.config = config or {}
        self.auth_manager = AuthManager(credentials_file, token_file)
        self.service = None
        self.template_name = None  # Subclass should set this

    def authenticate(self) -> googleapiclient.discovery.Resource:
        """
        Authenticate with Gmail API.

        Delegates to AuthManager for OAuth 2.0 handling.
        Caches service object for reuse.

        Returns:
            Gmail API service resource
        """
        if self.service is None:
            self.service = self.auth_manager.authenticate()
        return self.service

    @abstractmethod
    def search_emails(self) -> List[Dict]:
        """
        Search Gmail for relevant emails.

        Must be implemented by subclass with domain-specific search logic.

        Returns:
            List of Gmail message dicts containing:
            - 'id': Message ID
            - 'threadId': Thread ID
            - 'labelIds': List of label IDs
            - 'snippet': Message preview
            - 'internalDate': Timestamp
            - (others from Gmail API)

        Example (Utility Analyzer):
            query = 'from:(pseg.com OR ecrm-mail.verizon.com) subject:(bill OR statement)'
            return self.search_emails_generic(query, max_results=10)
        """
        pass

    @abstractmethod
    def parse_documents(self, emails: List[Dict]) -> List[Dict]:
        """
        Parse extracted emails into structured financial data.

        Must be implemented by subclass with domain-specific parsing logic.

        Args:
            emails: List of Gmail message dicts from search_emails()

        Returns:
            List of parsed document dicts with structure:
            {
                'provider': 'Company Name',
                'account_id': 'XXXX0906',
                'bill_date': '2025-02-28',
                'amount_due': 156.43,
                'email_date': '2025-02-28T14:22:00Z',
                ... (domain-specific fields)
            }

        Example (Utility Analyzer):
            Return list of utility bills with amount_due, usage, charges
        """
        pass

    def search_emails_generic(self,
                             query: str,
                             max_results: int = 10) -> List[Dict]:
        """
        Generic email search implementation.

        Uses Gmail API to search for emails matching a query.
        Can be used by subclasses or overridden with custom logic.

        Args:
            query: Gmail search query (e.g., 'from:pseg.com subject:bill')
            max_results: Maximum emails to return (default 10)

        Returns:
            List of Gmail message dicts

        Example:
            emails = self.search_emails_generic(
                'from:pseg.com subject:(bill OR statement)',
                max_results=10
            )
        """
        try:
            self.authenticate()  # Ensure authenticated

            response = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = response.get('messages', [])
            print(f"✓ Found {len(messages)} emails for query: {query}")

            # Get full message details (not just metadata)
            full_messages = []
            for message in messages:
                try:
                    full_message = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    full_messages.append(full_message)
                except Exception as e:
                    print(f"Warning: Could not fetch message {message['id']}: {e}")
                    continue

            return full_messages

        except Exception as e:
            print(f"Error searching emails: {e}")
            return []

    def export_json(self,
                   data: List[Dict],
                   filename: str) -> str:
        """
        Export parsed data to JSON file.

        Standard format for all analyzers.

        Args:
            data: List of parsed document dicts
            filename: Output filename (e.g., 'data/utility_data.json')

        Returns:
            Path to exported file

        Raises:
            IOError: If file write fails
        """
        try:
            # Ensure directory exists
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # Write JSON
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            print(f"✓ Exported {len(data)} records to {filename}")
            return filename

        except Exception as e:
            print(f"Error exporting JSON: {e}")
            raise

    def run(self) -> Tuple[List[Dict], str, str]:
        """
        Orchestrate full analysis pipeline.

        Template method pattern:
        1. Search emails
        2. Parse documents
        3. Export JSON
        4. Generate HTML report (future)

        Returns:
            Tuple of:
            - List[Dict]: Parsed data
            - str: Path to exported JSON file
            - str: Path to generated HTML report (or '' if not yet implemented)

        Raises:
            Exception: If any step fails
        """
        try:
            print(f"\n{'='*60}")
            print(f"Starting {self.analyzer_name}")
            print(f"{'='*60}")

            # Step 1: Search emails
            print(f"\n→ Searching for relevant emails...")
            emails = self.search_emails()
            if not emails:
                print(f"⚠ No emails found")
                return [], '', ''

            # Step 2: Parse documents
            print(f"\n→ Parsing documents...")
            data = self.parse_documents(emails)
            if not data:
                print(f"⚠ No data extracted")
                return [], '', ''

            print(f"✓ Extracted {len(data)} documents")

            # Step 3: Export JSON
            print(f"\n→ Exporting data...")
            json_file = self.export_json(
                data,
                f"data/{self.analyzer_name.lower()}_data.json"
            )

            # Step 4: Generate HTML report
            # TODO: Implement with Jinja2 templates
            html_file = ''  # For now, not implemented

            print(f"\n✓ {self.analyzer_name} complete")
            return data, json_file, html_file

        except Exception as e:
            print(f"✗ Error in {self.analyzer_name}: {e}")
            raise

    def get_metadata(self) -> Dict:
        """
        Return analyzer metadata.

        Used for discovery and plugin systems (future agentic orchestrator).

        Returns:
            Dict with:
            - name: Analyzer name
            - version: Analyzer version
            - supported_providers: List of companies this analyzer handles
            - output_schema: Description of output structure
        """
        return {
            'name': self.analyzer_name,
            'version': '1.0.0',
            'supported_providers': [],
            'output_schema': {},
        }
