"""Email and HTML parsing utilities.

Provides common functions for extracting data from email bodies and HTML.
Extracted from analyzer-specific code to be reused across analyzers.
"""

import base64
import re
from typing import Optional, Dict, List, Tuple
from html.parser import HTMLParser
from datetime import datetime


class EmailParser:
    """Utilities for parsing Gmail message content."""

    @staticmethod
    def decode_email_body(message_data: Dict) -> str:
        """
        Extract and decode email body from Gmail message.

        Gmail API returns body as base64url-encoded data in message['payload']['body']['data'].
        This function decodes it to readable text.

        Args:
            message_data: Gmail message dict with 'payload' key

        Returns:
            Decoded email body as string (HTML or plain text)

        Raises:
            ValueError: If body structure is unexpected
        """
        try:
            payload = message_data.get('payload', {})

            # Try direct body first
            if 'body' in payload and 'data' in payload['body']:
                encoded = payload['body']['data']
                # Gmail uses base64url encoding (replace - with + and _ with /)
                encoded = encoded.replace('-', '+').replace('_', '/')
                return base64.urlsafe_b64decode(encoded).decode('utf-8', errors='ignore')

            # If not in direct body, try parts (for multipart emails)
            if 'parts' in payload:
                for part in payload['parts']:
                    if 'body' in part and 'data' in part['body']:
                        # Found the body part
                        encoded = part['body']['data']
                        encoded = encoded.replace('-', '+').replace('_', '/')
                        return base64.urlsafe_b64decode(encoded).decode('utf-8', errors='ignore')

            return ""  # Empty body if nothing found
        except Exception as e:
            print(f"Error decoding email body: {e}")
            return ""

    @staticmethod
    def get_header(headers: List[Dict], header_name: str) -> Optional[str]:
        """
        Extract a specific header from email headers.

        Gmail API returns headers as a list of dicts with 'name' and 'value' keys.

        Args:
            headers: List of header dicts from message['payload']['headers']
            header_name: Name of header to find (case-insensitive)

        Returns:
            Header value or None if not found
        """
        header_name_lower = header_name.lower()
        for header in headers:
            if header.get('name', '').lower() == header_name_lower:
                return header.get('value', '').strip()
        return None

    @staticmethod
    def extract_email_address(email_string: str) -> Optional[str]:
        """
        Extract email address from 'Name <email@domain.com>' format.

        Args:
            email_string: Email string (may include name and angle brackets)

        Returns:
            Email address or None if not found
        """
        match = re.search(r'<([^>]+)>', email_string)
        if match:
            return match.group(1)
        # If no angle brackets, try to extract plain email
        if '@' in email_string:
            return email_string.strip()
        return None

    @staticmethod
    def extract_domain(email_address: str) -> Optional[str]:
        """
        Extract domain from email address.

        Args:
            email_address: Email address

        Returns:
            Domain portion (after @) or None
        """
        if '@' not in email_address:
            return None
        return email_address.split('@')[1].lower()

    @staticmethod
    def extract_text_between(text: str, start: str, end: str) -> Optional[str]:
        """
        Extract text between two delimiters.

        Args:
            text: Text to search in
            start: Starting delimiter
            end: Ending delimiter

        Returns:
            Text between delimiters (or None if not found)
        """
        start_idx = text.find(start)
        if start_idx == -1:
            return None
        start_idx += len(start)

        end_idx = text.find(end, start_idx)
        if end_idx == -1:
            return None

        return text[start_idx:end_idx].strip()

    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """
        Extract all numbers (floats and ints) from text.

        Args:
            text: Text to search in

        Returns:
            List of numbers found
        """
        pattern = r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?'
        matches = re.findall(pattern, text)
        try:
            return [float(m) for m in matches]
        except ValueError:
            return []

    @staticmethod
    def extract_dollar_amounts(text: str) -> List[float]:
        """
        Extract dollar amounts from text (e.g., $123.45).

        Args:
            text: Text to search in

        Returns:
            List of dollar amounts found
        """
        pattern = r'\$[-+]?[0-9]*\.?[0-9]+'
        matches = re.findall(pattern, text)
        try:
            return [float(m.replace('$', '')) for m in matches]
        except ValueError:
            return []

    @staticmethod
    def parse_date(date_string: str,
                   formats: Optional[List[str]] = None) -> Optional[datetime]:
        """
        Parse date string with multiple format support.

        Args:
            date_string: Date string to parse
            formats: List of datetime formats to try. Defaults to common formats.

        Returns:
            Datetime object or None if parsing fails
        """
        if formats is None:
            formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%m/%d/%y',
                '%B %d, %Y',
                '%b %d, %Y',
                '%d %b %Y',
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y %H:%M:%S',
            ]

        for fmt in formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue

        return None  # Could not parse with any format

    @staticmethod
    def clean_whitespace(text: str) -> str:
        """
        Normalize whitespace: collapse multiple spaces/newlines.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        return ' '.join(text.split())


class HTMLTableParser(HTMLParser):
    """Parse HTML tables into structured data."""

    def __init__(self):
        """Initialize parser."""
        super().__init__()
        self.tables = []
        self.current_table = None
        self.current_row = None
        self.current_cell = None

    def handle_starttag(self, tag: str, attrs):
        """Handle opening HTML tags."""
        if tag == 'table':
            self.current_table = {'rows': []}
        elif tag == 'tr' and self.current_table is not None:
            self.current_row = []
        elif tag in ('td', 'th') and self.current_row is not None:
            self.current_cell = {'text': '', 'tag': tag}

    def handle_data(self, data: str):
        """Handle text content between tags."""
        if self.current_cell is not None:
            self.current_cell['text'] += data.strip()

    def handle_endtag(self, tag: str):
        """Handle closing HTML tags."""
        if tag in ('td', 'th') and self.current_cell is not None:
            self.current_row.append(self.current_cell['text'])
            self.current_cell = None
        elif tag == 'tr' and self.current_row is not None:
            if self.current_table is not None:
                self.current_table['rows'].append(self.current_row)
            self.current_row = None
        elif tag == 'table' and self.current_table is not None:
            self.tables.append(self.current_table)
            self.current_table = None

    def get_tables(self) -> List[List[List[str]]]:
        """
        Get parsed tables.

        Returns:
            List of tables, where each table is a list of rows,
            and each row is a list of cell values
        """
        return [table['rows'] for table in self.tables]


def parse_html_tables(html: str) -> List[List[List[str]]]:
    """
    Parse HTML tables from an HTML string.

    Args:
        html: HTML string containing tables

    Returns:
        List of tables (each table is a list of rows with cells)
    """
    parser = HTMLTableParser()
    try:
        parser.feed(html)
    except Exception as e:
        print(f"Error parsing HTML tables: {e}")
        return []
    return parser.get_tables()
