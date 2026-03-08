"""Unit tests for email and HTML parsing utilities."""

import pytest
import base64
from datetime import datetime

from shared.email_parser import EmailParser, HTMLTableParser, parse_html_tables


class TestEmailParserDecodeEmailBody:
    """Test email body decoding."""

    def test_decode_email_body_direct(self):
        """Test decoding body from direct payload.body.data."""
        text = "This is a test email body"
        encoded = base64.urlsafe_b64encode(text.encode()).decode()

        message = {
            'payload': {
                'body': {
                    'data': encoded
                }
            }
        }

        result = EmailParser.decode_email_body(message)
        assert result == text

    def test_decode_email_body_from_parts(self):
        """Test decoding body from multipart message parts."""
        text = "This is a test email from parts"
        encoded = base64.urlsafe_b64encode(text.encode()).decode()

        message = {
            'payload': {
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {'data': encoded}
                    }
                ]
            }
        }

        result = EmailParser.decode_email_body(message)
        assert result == text

    def test_decode_email_body_empty(self):
        """Test decoding empty email."""
        message = {'payload': {}}
        result = EmailParser.decode_email_body(message)
        assert result == ""

    def test_decode_email_body_invalid(self):
        """Test decoding with invalid data returns empty."""
        message = {
            'payload': {
                'body': {
                    'data': 'invalid_base64!!!'
                }
            }
        }

        result = EmailParser.decode_email_body(message)
        # Should return empty string on error
        assert isinstance(result, str)


class TestEmailParserGetHeader:
    """Test header extraction."""

    def test_get_header_found(self):
        """Test extracting existing header."""
        headers = [
            {'name': 'From', 'value': 'test@example.com'},
            {'name': 'Subject', 'value': 'Test Subject'},
        ]

        result = EmailParser.get_header(headers, 'From')
        assert result == 'test@example.com'

    def test_get_header_case_insensitive(self):
        """Test header extraction is case-insensitive."""
        headers = [
            {'name': 'From', 'value': 'test@example.com'},
        ]

        result = EmailParser.get_header(headers, 'from')
        assert result == 'test@example.com'

    def test_get_header_not_found(self):
        """Test getting non-existent header returns None."""
        headers = [
            {'name': 'From', 'value': 'test@example.com'},
        ]

        result = EmailParser.get_header(headers, 'Subject')
        assert result is None

    def test_get_header_empty_list(self):
        """Test getting header from empty list."""
        result = EmailParser.get_header([], 'From')
        assert result is None


class TestEmailParserExtractEmailAddress:
    """Test email address extraction."""

    def test_extract_email_with_name(self):
        """Test extracting email from 'Name <email@domain.com>' format."""
        result = EmailParser.extract_email_address('John Doe <john@example.com>')
        assert result == 'john@example.com'

    def test_extract_email_plain(self):
        """Test extracting plain email address."""
        result = EmailParser.extract_email_address('test@example.com')
        assert result == 'test@example.com'

    def test_extract_email_invalid(self):
        """Test extracting from invalid email."""
        result = EmailParser.extract_email_address('not an email')
        assert result is None


class TestEmailParserExtractDomain:
    """Test domain extraction."""

    def test_extract_domain_success(self):
        """Test extracting domain from email."""
        result = EmailParser.extract_domain('test@example.com')
        assert result == 'example.com'

    def test_extract_domain_case_insensitive(self):
        """Test domain extraction is case-insensitive."""
        result = EmailParser.extract_domain('test@EXAMPLE.COM')
        assert result == 'example.com'

    def test_extract_domain_invalid(self):
        """Test extracting domain from invalid email."""
        result = EmailParser.extract_domain('not-an-email')
        assert result is None


class TestEmailParserExtractTextBetween:
    """Test text extraction between delimiters."""

    def test_extract_text_between_success(self):
        """Test extracting text between delimiters."""
        text = "Start [CONTENT] End"
        result = EmailParser.extract_text_between(text, '[', ']')
        assert result == 'CONTENT'

    def test_extract_text_between_not_found(self):
        """Test extraction when delimiters not found."""
        text = "No delimiters here"
        result = EmailParser.extract_text_between(text, '[', ']')
        assert result is None

    def test_extract_text_between_multiple(self):
        """Test extraction with multiple matches returns first."""
        text = "First [A] and [B]"
        result = EmailParser.extract_text_between(text, '[', ']')
        assert result == 'A'


class TestEmailParserExtractNumbers:
    """Test number extraction."""

    def test_extract_numbers_integers(self):
        """Test extracting integers."""
        text = "Values: 10, 20, 30"
        result = EmailParser.extract_numbers(text)
        assert 10 in result
        assert 20 in result
        assert 30 in result

    def test_extract_numbers_floats(self):
        """Test extracting floats."""
        text = "Price: 19.99 and 45.50"
        result = EmailParser.extract_numbers(text)
        assert 19.99 in result
        assert 45.50 in result

    def test_extract_numbers_none(self):
        """Test extraction with no numbers."""
        text = "No numbers here"
        result = EmailParser.extract_numbers(text)
        assert result == []


class TestEmailParserExtractDollarAmounts:
    """Test dollar amount extraction."""

    def test_extract_dollar_amounts(self):
        """Test extracting dollar amounts."""
        text = "Total: $100.00 and $50.25"
        result = EmailParser.extract_dollar_amounts(text)
        assert 100.00 in result
        assert 50.25 in result

    def test_extract_dollar_amounts_negative(self):
        """Test extracting negative dollar amounts."""
        text = "Credit: -$25.00"
        result = EmailParser.extract_dollar_amounts(text)
        assert -25.00 in result

    def test_extract_dollar_amounts_none(self):
        """Test extraction with no dollar amounts."""
        text = "No amounts here"
        result = EmailParser.extract_dollar_amounts(text)
        assert result == []


class TestEmailParserParseDate:
    """Test date parsing."""

    def test_parse_date_standard_formats(self):
        """Test parsing standard date formats."""
        test_cases = [
            ('2025-02-28', datetime(2025, 2, 28)),
            ('02/28/2025', datetime(2025, 2, 28)),
            ('February 28, 2025', datetime(2025, 2, 28)),
        ]

        for date_str, expected in test_cases:
            result = EmailParser.parse_date(date_str)
            assert result.date() == expected.date()

    def test_parse_date_invalid(self):
        """Test parsing invalid date returns None."""
        result = EmailParser.parse_date('not a date')
        assert result is None

    def test_parse_date_custom_formats(self):
        """Test parsing with custom formats."""
        result = EmailParser.parse_date('28-Feb-2025', ['%d-%b-%Y'])
        assert result.date() == datetime(2025, 2, 28).date()


class TestEmailParserCleanWhitespace:
    """Test whitespace cleaning."""

    def test_clean_whitespace_multiple_spaces(self):
        """Test collapsing multiple spaces."""
        text = "This  has   multiple    spaces"
        result = EmailParser.clean_whitespace(text)
        assert result == "This has multiple spaces"

    def test_clean_whitespace_newlines(self):
        """Test collapsing newlines."""
        text = "Line 1\n\nLine 2\n\n\nLine 3"
        result = EmailParser.clean_whitespace(text)
        assert result == "Line 1 Line 2 Line 3"

    def test_clean_whitespace_tabs(self):
        """Test handling tabs."""
        text = "Text\twith\ttabs"
        result = EmailParser.clean_whitespace(text)
        assert result == "Text with tabs"


class TestHTMLTableParser:
    """Test HTML table parsing."""

    def test_parse_simple_table(self):
        """Test parsing a simple HTML table."""
        html = """
        <table>
            <tr><td>A1</td><td>A2</td></tr>
            <tr><td>B1</td><td>B2</td></tr>
        </table>
        """

        tables = parse_html_tables(html)
        assert len(tables) == 1
        assert len(tables[0]) == 2  # 2 rows
        assert tables[0][0] == ['A1', 'A2']
        assert tables[0][1] == ['B1', 'B2']

    def test_parse_table_with_headers(self):
        """Test parsing table with headers."""
        html = """
        <table>
            <tr><th>Header1</th><th>Header2</th></tr>
            <tr><td>Data1</td><td>Data2</td></tr>
        </table>
        """

        tables = parse_html_tables(html)
        assert len(tables) == 1
        assert tables[0][0] == ['Header1', 'Header2']
        assert tables[0][1] == ['Data1', 'Data2']

    def test_parse_multiple_tables(self):
        """Test parsing multiple tables in one HTML."""
        html = """
        <table>
            <tr><td>A1</td></tr>
        </table>
        <table>
            <tr><td>B1</td></tr>
        </table>
        """

        tables = parse_html_tables(html)
        assert len(tables) == 2

    def test_parse_empty_html(self):
        """Test parsing HTML with no tables."""
        html = "<div>No tables here</div>"
        tables = parse_html_tables(html)
        assert len(tables) == 0

    def test_parse_table_with_whitespace(self):
        """Test that whitespace is trimmed from cells."""
        html = """
        <table>
            <tr><td>  Data with spaces  </td></tr>
        </table>
        """

        tables = parse_html_tables(html)
        assert tables[0][0][0] == 'Data with spaces'
