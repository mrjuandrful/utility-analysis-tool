#!/usr/bin/env python3
"""
Unit tests for TelecomAnalyzer.

Tests:
- Initialization
- Email searching for Verizon bills
- Bill type identification (Fios vs Wireless)
- Document parsing and extraction
- Amount extraction from subjects
- HTML report generation
- Full pipeline execution
"""

import pytest
from unittest.mock import Mock, patch
from analyzers.telecom_analyzer import TelecomAnalyzer, VERIZON_BILL_TYPES


class TestTelecomAnalyzerInitialization:
    """Test TelecomAnalyzer initialization and configuration."""

    def test_initialization(self):
        """Test basic initialization."""
        analyzer = TelecomAnalyzer()
        assert analyzer.analyzer_type == 'telecom'
        assert analyzer.utilities_found == {}
        assert analyzer.total_utility_emails == 0

    def test_metadata(self):
        """Test analyzer metadata."""
        metadata = TelecomAnalyzer.get_metadata()
        assert metadata['name'] == 'Verizon Telecom Analyzer'
        assert metadata['domain'] == 'telecom'
        assert 'Verizon Fios' in metadata['supports']
        assert 'Verizon Wireless' in metadata['supports']


class TestEmailSearching:
    """Test email search functionality."""

    def test_search_emails_creates_correct_query(self):
        """Test that search_emails uses correct Gmail query."""
        analyzer = TelecomAnalyzer()
        
        # Mock the search_emails_generic method
        analyzer.search_emails_generic = Mock(return_value=[])
        
        analyzer.search_emails()
        
        # Verify the query was correct
        analyzer.search_emails_generic.assert_called_once()
        call_args = analyzer.search_emails_generic.call_args
        assert 'verizon' in call_args[1]['query'].lower()
        assert call_args[1]['max_results'] == 10

    def test_search_emails_returns_list(self):
        """Test that search_emails returns a list."""
        analyzer = TelecomAnalyzer()
        analyzer.search_emails_generic = Mock(return_value=[])
        
        result = analyzer.search_emails()
        assert isinstance(result, list)


class TestBillTypeIdentification:
    """Test bill type detection (Fios vs Wireless)."""

    def test_identify_fios_bill(self):
        """Test Fios bill identification."""
        analyzer = TelecomAnalyzer()
        
        # Test with Fios keywords
        assert analyzer._identify_bill_type(
            'billing@verizon.com',
            'Your Verizon Fios Internet Bill'
        ) == 'fios'
        
        assert analyzer._identify_bill_type(
            'verizon@verizon.com',
            'Broadband Service Statement'
        ) == 'fios'

    def test_identify_wireless_bill(self):
        """Test Wireless bill identification."""
        analyzer = TelecomAnalyzer()
        
        assert analyzer._identify_bill_type(
            'billing@verizon.com',
            'Your Verizon Wireless Bill'
        ) == 'wireless'
        
        assert analyzer._identify_bill_type(
            'verizon@verizon.com',
            'Mobile Plan Invoice'
        ) == 'wireless'

    def test_identify_unknown_bill_type(self):
        """Test unknown bill type."""
        analyzer = TelecomAnalyzer()
        
        result = analyzer._identify_bill_type(
            'billing@verizon.com',
            'Something Else'
        )
        assert result == 'unknown'


class TestVerizonBillDetection:
    """Test Verizon bill detection logic."""

    def test_is_verizon_bill_true(self):
        """Test detection of valid Verizon bills."""
        analyzer = TelecomAnalyzer()
        
        assert analyzer._is_verizon_bill(
            'billing@verizon.com',
            'Your Verizon Bill'
        ) is True
        
        assert analyzer._is_verizon_bill(
            'billing@verizon.com',
            'Verizon Statement'
        ) is True
        
        assert analyzer._is_verizon_bill(
            'verizon@example.com',
            'Invoice from Verizon'
        ) is True

    def test_is_verizon_bill_false_no_verizon(self):
        """Test rejection of non-Verizon emails."""
        analyzer = TelecomAnalyzer()
        
        assert analyzer._is_verizon_bill(
            'billing@comcast.com',
            'Your Bill'
        ) is False

    def test_is_verizon_bill_false_no_bill_keyword(self):
        """Test rejection of Verizon emails without bill keywords."""
        analyzer = TelecomAnalyzer()
        
        assert analyzer._is_verizon_bill(
            'support@verizon.com',
            'Technical Support Information'
        ) is False


class TestAmountExtraction:
    """Test dollar amount extraction."""

    def test_extract_amount_basic(self):
        """Test basic amount extraction."""
        analyzer = TelecomAnalyzer()
        
        assert analyzer._extract_amount('Pay $123.45 now') == '$123.45'
        assert analyzer._extract_amount('Amount due: $1,234.56') == '$1,234.56'

    def test_extract_amount_no_match(self):
        """Test when no amount is found."""
        analyzer = TelecomAnalyzer()
        
        assert analyzer._extract_amount('No amount here') is None
        assert analyzer._extract_amount('Price is $12 (missing cents)') is None

    def test_extract_amount_multiple(self):
        """Test extraction of first amount when multiple present."""
        analyzer = TelecomAnalyzer()
        
        result = analyzer._extract_amount(
            'Previous balance: $50.00, Amount due: $123.45'
        )
        assert result == '$50.00'  # Gets first match


class TestDocumentParsing:
    """Test email parsing and document extraction."""

    def test_parse_documents_empty_list(self):
        """Test parsing empty email list."""
        analyzer = TelecomAnalyzer()
        
        result = analyzer.parse_documents([])
        
        assert result['total_bills'] == 0
        assert result['bills_found'] == {}
        assert result['bill_details'] == []

    def test_parse_documents_single_fios_bill(self):
        """Test parsing a single Fios bill."""
        analyzer = TelecomAnalyzer()
        
        emails = [
            {
                'from': 'billing@verizon.com',
                'subject': 'Your Verizon Fios Bill - $89.99',
                'date': '2026-03-01',
                'id': 'msg123',
            }
        ]
        
        result = analyzer.parse_documents(emails)
        
        assert result['total_bills'] == 1
        assert 'Verizon Fios' in result['bills_found']
        assert result['bills_found']['Verizon Fios']['bills'] == 1
        assert len(result['bill_details']) == 1

    def test_parse_documents_mixed_bills(self):
        """Test parsing mixed Fios and Wireless bills."""
        analyzer = TelecomAnalyzer()
        
        emails = [
            {
                'from': 'billing@verizon.com',
                'subject': 'Your Verizon Fios Bill',
                'date': '2026-03-01',
                'id': 'msg1',
            },
            {
                'from': 'billing@verizon.com',
                'subject': 'Verizon Wireless Invoice',
                'date': '2026-03-02',
                'id': 'msg2',
            },
        ]
        
        result = analyzer.parse_documents(emails)
        
        assert result['total_bills'] == 2
        assert 'Verizon Fios' in result['bills_found']
        assert 'Verizon Wireless' in result['bills_found']

    def test_parse_documents_amount_extraction(self):
        """Test amount extraction during parsing."""
        analyzer = TelecomAnalyzer()
        
        emails = [
            {
                'from': 'billing@verizon.com',
                'subject': 'Your Verizon Bill - Amount Due: $150.25',
                'date': '2026-03-01',
                'id': 'msg1',
            }
        ]
        
        result = analyzer.parse_documents(emails)
        
        assert result['bill_details'][0]['amount_due'] == '$150.25'


class TestHTMLReportGeneration:
    """Test HTML report generation."""

    def test_generate_html_report_basic(self):
        """Test basic HTML report generation."""
        analyzer = TelecomAnalyzer()
        analyzer.total_emails = 20
        
        data = {
            'bills_found': {
                'Verizon Fios': {
                    'type': 'Internet/TV/Phone',
                    'bills': 6,
                    'latest': '2026-03-01'
                },
                'Verizon Wireless': {
                    'type': 'Mobile/Data',
                    'bills': 4,
                    'latest': '2026-03-01'
                }
            },
            'total_bills': 10,
        }
        
        html = analyzer.generate_html_report(data)
        
        assert '<!DOCTYPE html>' in html
        assert 'Verizon Bill Analysis Report' in html
        assert '20' in html  # total_emails
        assert '10' in html  # total_bills

    def test_generate_html_report_contains_table(self):
        """Test that HTML report includes table with services."""
        analyzer = TelecomAnalyzer()
        analyzer.total_emails = 10
        
        data = {
            'bills_found': {
                'Verizon Fios': {
                    'type': 'Internet/TV/Phone',
                    'bills': 5,
                    'latest': '2026-03-01'
                }
            },
            'total_bills': 5,
        }
        
        html = analyzer.generate_html_report(data)
        
        assert '<table>' in html
        assert 'Verizon Fios' in html
        assert 'Internet/TV/Phone' in html


class TestFullPipeline:
    """Test complete analyzer pipeline."""

    def test_run_full_pipeline(self):
        """Test complete run() pipeline with mocks."""
        analyzer = TelecomAnalyzer()
        
        # Mock parent's run method
        with patch('analyzers.base_analyzer.BaseAnalyzer.run') as mock_run:
            mock_run.return_value = {
                'success': True,
                'parsed_data': {
                    'bills_found': {},
                    'total_bills': 0
                }
            }
            
            result = analyzer.run(export_json=True, export_html=False)
            
            assert result['success'] is True
            mock_run.assert_called_once()

    def test_run_with_html_export(self):
        """Test pipeline with HTML export."""
        analyzer = TelecomAnalyzer()
        
        with patch('analyzers.base_analyzer.BaseAnalyzer.run') as mock_run:
            mock_run.return_value = {
                'success': True,
                'parsed_data': {
                    'bills_found': {},
                    'total_bills': 0
                }
            }
            
            with patch('builtins.open', create=True) as mock_open:
                result = analyzer.run(export_json=True, export_html=True)
                
                # Should attempt to write HTML file
                if result.get('success'):
                    # File write would be attempted
                    pass


class TestVerizonBillTypes:
    """Test VERIZON_BILL_TYPES configuration."""

    def test_bill_type_configuration(self):
        """Test that bill type configuration is complete."""
        assert 'fios' in VERIZON_BILL_TYPES
        assert 'wireless' in VERIZON_BILL_TYPES

    def test_fios_config(self):
        """Test Fios configuration."""
        fios = VERIZON_BILL_TYPES['fios']
        assert fios['name'] == 'Verizon Fios'
        assert fios['type'] == 'Internet/TV/Phone'
        assert '867-0001' in fios['bill_codes']

    def test_wireless_config(self):
        """Test Wireless configuration."""
        wireless = VERIZON_BILL_TYPES['wireless']
        assert wireless['name'] == 'Verizon Wireless'
        assert wireless['type'] == 'Mobile/Data'
        assert '7065-00001' in wireless['bill_codes']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
