#!/usr/bin/env python3
"""
Gmail Utility Analyzer

Inherits from BaseAnalyzer to search Gmail for utility company emails
and parse them into a structured format.

Uses Jinja2 templates for HTML report generation instead of inline HTML.

Supports companies like PSEG, JCP&L, Verizon, Comcast, etc.
"""

from typing import Dict, List
from analyzers.base_analyzer import BaseAnalyzer
from shared.html_generator import HTMLGenerator


# Utility company patterns and metadata
UTILITY_COMPANIES = {
    'pseg': {'name': 'PSEG', 'type': 'Electric/Gas', 'state': 'NJ'},
    'jcp&l': {'name': 'JCP&L', 'type': 'Electric', 'state': 'NJ'},
    'orange': {'name': 'Orange & Rockland', 'type': 'Electric/Gas', 'state': 'NY/NJ'},
    'con edison': {'name': 'Con Edison', 'type': 'Electric/Gas', 'state': 'NY'},
    'eversource': {'name': 'Eversource', 'type': 'Electric/Gas', 'state': 'MA/CT'},
    'national grid': {'name': 'National Grid', 'type': 'Electric/Gas', 'state': 'NY/MA'},
    'verizon': {'name': 'Verizon', 'type': 'Internet/Phone', 'state': 'National'},
    'comcast': {'name': 'Comcast', 'type': 'Internet/TV', 'state': 'National'},
}


class GmailUtilityAnalyzer(BaseAnalyzer):
    """
    Analyzer for utility company emails from Gmail.

    Searches for emails mentioning bills, statements, or invoices,
    then identifies which utilities they're from.
    """

    def __init__(self, service=None):
        """Initialize the analyzer."""
        super().__init__(service=service)
        self.analyzer_type = 'utility'
        self.utilities_found = {}
        self.total_utility_emails = 0

    # ==================== DOMAIN-SPECIFIC: SEARCH ====================

    def search_emails(self) -> List[Dict]:
        """
        Search Gmail for utility-related emails.

        Looks for emails containing: bill, statement, invoice
        Returns basic metadata about found emails.
        """
        query = 'bill OR statement OR invoice'
        return self.search_emails_generic(query=query, max_results=10)

    # ==================== DOMAIN-SPECIFIC: PARSE ====================

    def parse_documents(self, emails: List[Dict]) -> Dict:
        """
        Parse email list to identify utilities and extract metadata.

        Returns structured data with:
        - utilities_found: Dict mapping company name to details
        - total_utility_emails: Count of utility-related emails
        - email_details: List of individual email metadata
        """
        utilities = {}
        email_details = []
        utility_count = 0

        for email in emails:
            from_addr = email.get('from', '')
            subject = email.get('subject', '')
            date = email.get('date', '')
            email_id = email.get('id', '')

            # Check if this is a utility email
            if self._is_utility_email(from_addr, subject):
                utility_count += 1

                # Identify which utility(ies) this email is from
                identified_utilities = self._identify_utilities_in_email(
                    from_addr, subject
                )

                # Store details about this email
                email_details.append({
                    'from': from_addr,
                    'subject': subject,
                    'date': date,
                    'id': email_id,
                    'utilities': identified_utilities,
                })

                # Accumulate utility company counts
                for company_name, company_info in identified_utilities.items():
                    if company_name not in utilities:
                        utilities[company_name] = {
                            'type': company_info['type'],
                            'state': company_info['state'],
                            'emails': 0,
                            'latest': date,
                        }
                    utilities[company_name]['emails'] += 1

        self.utilities_found = utilities
        self.total_utility_emails = utility_count

        return {
            'utilities_found': utilities,
            'total_utility_emails': utility_count,
            'email_details': email_details,
        }

    # ==================== HELPER METHODS ====================

    def _is_utility_email(self, from_addr: str, subject: str) -> bool:
        """
        Check if an email is from a known utility company.

        Args:
            from_addr: Email sender address
            subject: Email subject line

        Returns:
            True if email matches a known utility company pattern
        """
        email_text = (from_addr + ' ' + subject).lower()

        for company_key in UTILITY_COMPANIES.keys():
            if company_key in email_text:
                return True

        return False

    def _identify_utilities_in_email(self, from_addr: str, subject: str) -> Dict:
        """
        Identify which utility companies are mentioned in an email.

        Args:
            from_addr: Email sender address
            subject: Email subject line

        Returns:
            Dict mapping company names to their metadata
        """
        email_text = (from_addr + ' ' + subject).lower()
        identified = {}

        for company_key, company_info in UTILITY_COMPANIES.items():
            if company_key in email_text:
                company_name = company_info['name']
                if company_name not in identified:
                    identified[company_name] = {
                        'type': company_info['type'],
                        'state': company_info['state'],
                    }

        return identified

    def generate_html_report(self, data: Dict) -> str:
        """
        Generate an HTML report from parsed utility data using Jinja2 template.

        Args:
            data: Dict with utilities_found, total_utility_emails, etc.

        Returns:
            HTML string ready to write to file
        """
        utilities = data.get('utilities_found', {})
        utility_count = data.get('total_utility_emails', 0)

        # Calculate percentage
        email_percentage = round(
            (utility_count / max(self.total_emails, 1)) * 100, 1
        )

        # Prepare context for template
        context = {
            'timestamp': self.get_timestamp(),
            'total_emails': self.total_emails,
            'utilities_found': utilities,
            'utility_emails': utility_count,
            'utility_percentage': email_percentage,
        }

        # Render using Jinja2 template
        generator = HTMLGenerator()
        return generator.render('utility_report.html', context)

    def run(self, export_json: bool = True, export_html: bool = False) -> Dict:
        """
        Run the complete utility analysis pipeline.

        Orchestrates the inherited template method pattern:
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
            html_file = f'reports/utility_report_{self.run_timestamp}.html'

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
            Dict with name, description, version, supported domains
        """
        return {
            'name': 'Gmail Utility Analyzer',
            'description': 'Identifies utility companies from Gmail emails',
            'version': '2.0',
            'domain': 'utilities',
            'analyzer_type': 'utility',
            'supports': [
                'PSEG', 'JCP&L', 'Orange & Rockland', 'Con Edison',
                'Eversource', 'National Grid', 'Verizon', 'Comcast'
            ]
        }


def main():
    """CLI entry point for backwards compatibility."""
    analyzer = GmailUtilityAnalyzer()
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
