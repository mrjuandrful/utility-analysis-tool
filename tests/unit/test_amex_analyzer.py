#!/usr/bin/env python3
"""
Unit tests for AMEXAnalyzer.

Tests:
- Initialization
- Email searching for AMEX statements
- Statement detection
- Card type extraction
- Last 4 digits extraction
- Total spending extraction
- Transaction categorization
- Document parsing
- HTML report generation
- Full pipeline execution
"""

import pytest
from unittest.mock import Mock, patch
from analyzers.amex_analyzer import AMEXAnalyzer, AMEX_CATEGORIES


class TestAMEXAnalyzerInitialization:
    """Test AMEXAnalyzer initialization."""

    def test_initialization(self):
        """Test basic initialization."""
        analyzer = AMEXAnalyzer()
        assert analyzer.analyzer_type == 'credit_card'
        assert analyzer.card_type == 'AMEX'
        assert analyzer.statements_found == []
        assert analyzer.total_spending == 0.0
        assert analyzer.total_transactions == 0

    def test_metadata(self):
        """Test analyzer metadata."""
        metadata = AMEXAnalyzer.get_metadata()
        assert metadata['name'] == 'American Express Card Analyzer'
        assert metadata['domain'] == 'credit_card'
        assert 'AMEX Personal' in metadata['supports']
        assert 'AMEX Platinum' in metadata['supports']


class TestEmailSearching:
    """Test AMEX email search."""

    def test_search_emails_query(self):
        """Test that search_emails uses correct Gmail query."""
        analyzer = AMEXAnalyzer()
        analyzer.search_emails_generic = Mock(return_value=[])
        
        analyzer.search_emails()
        
        call_args = analyzer.search_emails_generic.call_args
        assert 'amex' in call_args[1]['query'].lower() or 'american' in call_args[1]['query'].lower()
        assert call_args[1]['max_results'] == 10


class TestStatementDetection:
    """Test AMEX statement detection."""

    def test_is_amex_statement_true(self):
        """Test detection of valid AMEX statements."""
        analyzer = AMEXAnalyzer()
        
        assert analyzer._is_amex_statement(
            'statement@americanexpress.com',
            'Your AMEX Statement'
        ) is True
        
        assert analyzer._is_amex_statement(
            'billing@amex.com',
            'Your Account Statement'
        ) is True

    def test_is_amex_statement_false_no_amex(self):
        """Test rejection of non-AMEX emails."""
        analyzer = AMEXAnalyzer()
        
        assert analyzer._is_amex_statement(
            'statement@visa.com',
            'Your Card Statement'
        ) is False

    def test_is_amex_statement_false_no_stmt_keyword(self):
        """Test rejection of AMEX emails without statement keywords."""
        analyzer = AMEXAnalyzer()
        
        assert analyzer._is_amex_statement(
            'support@amex.com',
            'Account Update Information'
        ) is False


class TestCardTypeExtraction:
    """Test card type extraction."""

    def test_extract_platinum_card(self):
        """Test Platinum card detection."""
        analyzer = AMEXAnalyzer()
        assert analyzer._extract_card_type('Your AMEX Platinum Statement') == 'Platinum'

    def test_extract_gold_card(self):
        """Test Gold card detection."""
        analyzer = AMEXAnalyzer()
        assert analyzer._extract_card_type('AMEX Gold Card Statement') == 'Gold'

    def test_extract_business_card(self):
        """Test Business card detection."""
        analyzer = AMEXAnalyzer()
        assert analyzer._extract_card_type('AMEX Business Statement') == 'Business'

    def test_extract_default_personal(self):
        """Test default to Personal if no type detected."""
        analyzer = AMEXAnalyzer()
        assert analyzer._extract_card_type('AMEX Statement') == 'Personal'


class TestLastFourExtraction:
    """Test last 4 digits extraction."""

    def test_extract_last_4_ending_in(self):
        """Test extraction with 'ending in' pattern."""
        analyzer = AMEXAnalyzer()
        result = analyzer._extract_last_4('Card ending in 1234')
        assert result == '1234'

    def test_extract_last_4_asterisks(self):
        """Test extraction with asterisks pattern."""
        analyzer = AMEXAnalyzer()
        result = analyzer._extract_last_4('XXXX XXXX XXXX 5678')
        assert result == '5678'

    def test_extract_last_4_not_found(self):
        """Test when no last 4 found."""
        analyzer = AMEXAnalyzer()
        result = analyzer._extract_last_4('No card numbers here')
        assert result == ''


class TestTotalSpendingExtraction:
    """Test total spending extraction."""

    def test_extract_spending_basic(self):
        """Test basic amount extraction."""
        analyzer = AMEXAnalyzer()
        assert analyzer._extract_total_spending('Total Due: $1,234.56') == 1234.56

    def test_extract_spending_no_comma(self):
        """Test amount without comma."""
        analyzer = AMEXAnalyzer()
        assert analyzer._extract_total_spending('Amount: $123.45') == 123.45

    def test_extract_spending_multiple(self):
        """Test extraction of first amount."""
        analyzer = AMEXAnalyzer()
        result = analyzer._extract_total_spending('Previous: $100.00, Current: $250.75')
        assert result == 100.00

    def test_extract_spending_not_found(self):
        """Test when no amount found."""
        analyzer = AMEXAnalyzer()
        assert analyzer._extract_total_spending('No amount here') == 0.0


class TestTransactionCategorization:
    """Test transaction category detection."""

    def test_categorize_restaurant(self):
        """Test restaurant categorization."""
        analyzer = AMEXAnalyzer()
        assert analyzer._categorize_transaction('Joe\'s Pizza Restaurant') == 'Restaurants'
        assert analyzer._categorize_transaction('CAFE ESPRESSO') == 'Restaurants'

    def test_categorize_travel(self):
        """Test travel categorization."""
        analyzer = AMEXAnalyzer()
        assert analyzer._categorize_transaction('UNITED AIRLINES') == 'Travel'
        assert analyzer._categorize_transaction('MARRIOTT HOTEL') == 'Travel'

    def test_categorize_groceries(self):
        """Test grocery categorization."""
        analyzer = AMEXAnalyzer()
        assert analyzer._categorize_transaction('WHOLE FOODS MARKET') == 'Groceries'

    def test_categorize_other(self):
        """Test default to Other."""
        analyzer = AMEXAnalyzer()
        assert analyzer._categorize_transaction('Random Purchase') == 'Other'


class TestDocumentParsing:
    """Test email parsing and data extraction."""

    def test_parse_documents_empty_list(self):
        """Test parsing empty email list."""
        analyzer = AMEXAnalyzer()
        
        result = analyzer.parse_documents([])
        
        assert result['total_spent'] == 0.0
        assert result['total_transactions'] == 0
        assert result['statements'] == []

    def test_parse_documents_single_statement(self):
        """Test parsing a single statement."""
        analyzer = AMEXAnalyzer()
        
        emails = [
            {
                'from': 'statement@amex.com',
                'subject': 'Your AMEX Platinum Statement - Total: $1,500.00',
                'date': '2026-03-01',
                'id': 'msg123',
            }
        ]
        
        result = analyzer.parse_documents(emails)
        
        assert result['total_spent'] == 1500.00
        assert result['total_transactions'] == 1
        assert len(result['statements']) == 1
        assert result['statements'][0]['total_amount'] == 1500.00

    def test_parse_documents_card_type_extraction(self):
        """Test card type extraction during parsing."""
        analyzer = AMEXAnalyzer()
        
        emails = [
            {
                'from': 'statement@amex.com',
                'subject': 'Your AMEX Gold Card Statement',
                'date': '2026-03-01',
                'id': 'msg1',
            }
        ]
        
        result = analyzer.parse_documents(emails)
        
        assert result['statements'][0]['card_type'] == 'Gold'

    def test_parse_documents_last_4_extraction(self):
        """Test last 4 extraction during parsing."""
        analyzer = AMEXAnalyzer()
        
        emails = [
            {
                'from': 'statement@amex.com',
                'subject': 'Your Card Ending in 5678 Statement',
                'date': '2026-03-01',
                'id': 'msg1',
            }
        ]
        
        result = analyzer.parse_documents(emails)
        
        assert result['statements'][0]['last_4'] == '5678'


class TestHTMLReportGeneration:
    """Test HTML report generation."""

    def test_generate_html_report_basic(self):
        """Test basic HTML report generation."""
        analyzer = AMEXAnalyzer()
        analyzer.total_emails = 10
        
        data = {
            'statements': [
                {
                    'from': 'statement@amex.com',
                    'subject': 'Statement',
                    'date': '2026-03-01',
                    'total_amount': 1500.00,
                }
            ],
            'total_spent': 1500.00,
            'total_transactions': 25,
            'spending_by_category': {},
        }
        
        html = analyzer.generate_html_report(data)
        
        assert html is not None
        assert len(html) > 0

    def test_rewards_estimation(self):
        """Test that HTML generation estimates rewards."""
        analyzer = AMEXAnalyzer()
        analyzer.total_emails = 10
        
        data = {
            'statements': [
                {'date': '2026-03-01', 'total_amount': 1000.00},
            ],
            'total_spent': 1000.00,
            'total_transactions': 10,
            'spending_by_category': {},
        }
        
        html = analyzer.generate_html_report(data)
        
        # Should generate valid HTML
        assert '<!DOCTYPE html>' in html or 'html' in html.lower()


class TestFullPipeline:
    """Test complete analyzer pipeline."""

    def test_run_full_pipeline(self):
        """Test complete run() pipeline."""
        analyzer = AMEXAnalyzer()
        
        with patch('analyzers.base_analyzer.BaseAnalyzer.run') as mock_run:
            mock_run.return_value = {
                'success': True,
                'parsed_data': {
                    'statements': [],
                    'total_spent': 0.0,
                }
            }
            
            result = analyzer.run(export_json=True, export_html=False)
            
            assert result['success'] is True
            mock_run.assert_called_once()


class TestAMEXCategories:
    """Test AMEX category configuration."""

    def test_categories_defined(self):
        """Test that spending categories are defined."""
        assert 'restaurants' in AMEX_CATEGORIES
        assert 'travel' in AMEX_CATEGORIES
        assert 'groceries' in AMEX_CATEGORIES
        assert 'other' in AMEX_CATEGORIES

    def test_category_keywords(self):
        """Test that categories have keywords."""
        for cat_key, cat_data in AMEX_CATEGORIES.items():
            assert 'name' in cat_data
            assert 'keywords' in cat_data
            assert isinstance(cat_data['keywords'], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
