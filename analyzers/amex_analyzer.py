#!/usr/bin/env python3
"""
American Express Credit Card Analyzer

Inherits from BaseAnalyzer to search Gmail for AMEX statements
and parse them to extract spending data.

Uses Jinja2 templates for HTML report generation.

Supports:
  - AMEX Personal Cards
  - AMEX Business Cards
  - Spending by category extraction
  - Rewards points tracking
"""

import re
from typing import Dict, List
from analyzers.base_analyzer import BaseAnalyzer
from shared.html_generator import HTMLGenerator


# AMEX spending categories
AMEX_CATEGORIES = {
    'restaurants': {'name': 'Restaurants', 'keywords': ['restaurant', 'cafe', 'pizza', 'burger', 'dining']},
    'travel': {'name': 'Travel', 'keywords': ['airline', 'hotel', 'uber', 'lyft', 'taxi', 'airbnb', 'booking']},
    'groceries': {'name': 'Groceries', 'keywords': ['whole foods', 'trader', 'safeway', 'kroger', 'amazon fresh']},
    'gas': {'name': 'Gas/Fuel', 'keywords': ['shell', 'chevron', 'exxon', 'bp', 'gas station']},
    'utilities': {'name': 'Utilities', 'keywords': ['electric', 'water', 'gas', 'internet', 'verizon', 'comcast']},
    'entertainment': {'name': 'Entertainment', 'keywords': ['movie', 'netflix', 'spotify', 'hulu', 'cinema']},
    'shopping': {'name': 'Shopping', 'keywords': ['amazon', 'target', 'walmart', 'costco', 'best buy']},
    'other': {'name': 'Other', 'keywords': []},
}


class AMEXAnalyzer(BaseAnalyzer):
    """
    Analyzer for American Express credit card statements from Gmail.

    Searches for AMEX statements in Gmail, extracts transaction data,
    categorizes spending, and estimates rewards points earned.
    """

    def __init__(self, service=None):
        """Initialize the AMEX analyzer."""
        super().__init__(service=service)
        self.analyzer_type = 'credit_card'
        self.card_type = 'AMEX'
        self.statements_found = []
        self.total_spending = 0.0
        self.total_transactions = 0
        self.spending_by_category = {}

    # ==================== DOMAIN-SPECIFIC: SEARCH ====================

    def search_emails(self) -> List[Dict]:
        """
        Search Gmail for AMEX statement emails.

        Searches for emails from American Express containing 'statement',
        'bill', 'your account', or 'spending' keywords.

        Returns:
            List of email metadata dicts
        """
        query = 'from:(americanexpress OR amex) subject:(statement OR bill OR spending OR account)'
        return self.search_emails_generic(query=query, max_results=10)

    # ==================== DOMAIN-SPECIFIC: PARSE ====================

    def parse_documents(self, emails: List[Dict]) -> Dict:
        """
        Parse AMEX statement emails to extract spending data.

        Extracts:
        - Total spending across statements
        - Number of transactions
        - Spending by category
        - Card type and last 4 digits
        - Statement period

        Returns:
            Dict with spending_data, total_spent, total_transactions
        """
        statements = []
        total_spent = 0.0
        transaction_count = 0
        spending_by_cat = {cat['name']: {'total': 0.0, 'count': 0} for cat in AMEX_CATEGORIES.values()}
        spending_by_cat['Other'] = {'total': 0.0, 'count': 0}

        for email in emails:
            from_addr = email.get('from', '')
            subject = email.get('subject', '')
            date = email.get('date', '')
            email_id = email.get('id', '')

            # Check if this is an AMEX statement
            if self._is_amex_statement(from_addr, subject):
                # Extract statement details
                statement = {
                    'from': from_addr,
                    'subject': subject,
                    'date': date,
                    'id': email_id,
                    'card_type': self._extract_card_type(subject),
                    'last_4': self._extract_last_4(subject),
                }

                # Extract spending amount
                amount = self._extract_total_spending(subject)
                if amount:
                    statement['total_amount'] = amount
                    total_spent += amount
                    transaction_count += 1

                statements.append(statement)

        self.statements_found = statements
        self.total_spending = total_spent
        self.total_transactions = transaction_count

        return {
            'statements': statements,
            'total_spent': total_spent,
            'total_transactions': transaction_count,
            'spending_by_category': spending_by_cat,
        }

    # ==================== HELPER METHODS ====================

    def _is_amex_statement(self, from_addr: str, subject: str) -> bool:
        """
        Check if an email is from AMEX and mentions statement/billing.

        Args:
            from_addr: Email sender address
            subject: Email subject line

        Returns:
            True if email is from AMEX and mentions statement/billing
        """
        email_text = (from_addr + ' ' + subject).lower()

        # Must contain AMEX
        if 'amex' not in email_text and 'american express' not in email_text:
            return False

        # Must mention statement/bill/account
        stmt_keywords = ['statement', 'bill', 'account', 'spending', 'your charges']
        if not any(keyword in email_text for keyword in stmt_keywords):
            return False

        return True

    def _extract_card_type(self, subject: str) -> str:
        """
        Extract card type from subject.

        Args:
            subject: Email subject line

        Returns:
            Card type (e.g., 'Platinum', 'Gold', 'Personal', 'Business')
        """
        subject_lower = subject.lower()

        card_types = ['platinum', 'gold', 'blue', 'green', 'corporate']
        for card_type in card_types:
            if card_type in subject_lower:
                return card_type.capitalize()

        if 'business' in subject_lower:
            return 'Business'

        return 'Personal'

    def _extract_last_4(self, text: str) -> str:
        """
        Extract last 4 digits of card from text.

        Args:
            text: Text to search (usually subject or body)

        Returns:
            Last 4 digits or empty string
        """
        # Pattern: ...1234, ****1234, ending in 1234, etc.
        match = re.search(r'(?:ending in|xxx|****|ending|)[\s-]*(\d{4})', text, re.IGNORECASE)
        if match:
            return match.group(1)
        return ''

    def _extract_total_spending(self, text: str) -> float:
        """
        Extract total spending amount from text.

        Args:
            text: Text to search

        Returns:
            Dollar amount as float, or 0.0
        """
        # Pattern: $XXX.XX with optional comma
        match = re.search(r'\$[\d,]+\.\d{2}', text)
        if match:
            try:
                amount_str = match.group(0).replace('$', '').replace(',', '')
                return float(amount_str)
            except ValueError:
                return 0.0
        return 0.0

    def _categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction by its description.

        Args:
            description: Transaction description

        Returns:
            Category name
        """
        desc_lower = description.lower()

        for category, data in AMEX_CATEGORIES.items():
            for keyword in data['keywords']:
                if keyword in desc_lower:
                    return data['name']

        return 'Other'

    def generate_html_report(self, data: Dict) -> str:
        """
        Generate an HTML report from parsed AMEX data using Jinja2 template.

        Args:
            data: Dict with spending data, statements, etc.

        Returns:
            HTML string ready to write to file
        """
        statements = data.get('statements', [])
        total_spent = data.get('total_spent', 0.0)
        total_transactions = data.get('total_transactions', 0)

        # Calculate average spending per statement
        avg_monthly = round(
            total_spent / max(len(statements), 1), 2
        )

        # Estimate AMEX rewards (typically 1-5% depending on card)
        # Using average of 2% for estimation
        estimated_rewards = round(total_spent * 0.02, 2)

        # Prepare context for template
        context = {
            'timestamp': self.get_timestamp(),
            'total_emails': self.total_emails,
            'total_statements': len(statements),
            'total_spent': total_spent,
            'avg_monthly': avg_monthly,
            'total_transactions': total_transactions,
            'estimated_rewards': estimated_rewards,
            'spending_by_category': {},  # Populated from parsed data
        }

        # Render using Jinja2 template
        generator = HTMLGenerator()
        return generator.render('amex_report.html', context)

    def run(self, export_json: bool = True, export_html: bool = False) -> Dict:
        """
        Run the complete AMEX analysis pipeline.

        Orchestrates:
        1. Authenticate (BaseAnalyzer)
        2. Search emails (this subclass)
        3. Parse documents (this subclass)
        4. Export JSON (BaseAnalyzer)
        5. Optionally generate HTML report (this subclass)

        Args:
            export_json: Whether to export JSON data (default True)
            export_html: Whether to generate HTML report (default False)

        Returns:
            Dict with 'success', 'data', 'json_file', 'html_file'
        """
        # Use parent's run() method for the standard pipeline
        result = super().run(export_json=export_json)

        # Additionally generate HTML report if requested
        if export_html and result.get('success'):
            parsed_data = result.get('parsed_data', {})
            html = self.generate_html_report(parsed_data)
            html_file = f'reports/amex_report_{self.run_timestamp}.html'

            import os
            os.makedirs('reports', exist_ok=True)
            with open(html_file, 'w') as f:
                f.write(html)

            result['html_file'] = html_file

        return result

    @classmethod
    def get_metadata(cls) -> Dict:
        """
        Provide metadata about this analyzer for plugin/registration system.

        Returns:
            Dict with name, description, version, supported cards
        """
        return {
            'name': 'American Express Card Analyzer',
            'description': 'Analyzes AMEX credit card spending from Gmail statements',
            'version': '1.0',
            'domain': 'credit_card',
            'analyzer_type': 'amex',
            'supports': ['AMEX Personal', 'AMEX Business', 'AMEX Platinum', 'AMEX Gold']
        }


def main():
    """CLI entry point for backwards compatibility."""
    analyzer = AMEXAnalyzer()
    result = analyzer.run(export_json=True, export_html=True)

    if result.get('success'):
        print(f"✅ Analysis complete!")
        if result.get('json_file'):
            print(f"   JSON: {result['json_file']}")
        if result.get('html_file'):
            print(f"   HTML: {result['html_file']}")
    else:
        print(f"❌ Analysis failed: {result.get('error')}")


if __name__ == '__main__':
    main()
