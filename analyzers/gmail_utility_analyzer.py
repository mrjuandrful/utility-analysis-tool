#!/usr/bin/env python3
"""
Gmail Utility Analyzer

Inherits from BaseAnalyzer to search Gmail for utility company emails
and parse them into a structured format.

Supports companies like PSEG, JCP&L, Verizon, Comcast, etc.
"""

from typing import Dict, List
from analyzers.base_analyzer import BaseAnalyzer


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

    def __init__(self):
        """Initialize the analyzer."""
        super().__init__(analyzer_name='GmailUtilityAnalyzer')
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
        Generate an HTML report from parsed utility data.

        Args:
            data: Dict with utilities_found, total_utility_emails, etc.

        Returns:
            HTML string ready to write to file
        """
        utilities = data.get('utilities_found', {})
        timestamp = self.get_timestamp()
        total_emails = self.total_emails
        utility_count = data.get('total_utility_emails', 0)

        # Calculate percentage
        email_percentage = round(
            (utility_count / max(total_emails, 1)) * 100, 1
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Gmail Utility Analysis Report</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f4f8; color: #1a1a2e; }}

  header {{
    background: linear-gradient(135deg, #1F4E79 0%, #2E75B6 100%);
    color: white; padding: 28px 40px;
  }}
  header h1 {{ font-size: 1.7rem; font-weight: 700; }}
  header p  {{ font-size: 0.95rem; opacity: 0.85; margin-top: 6px; }}

  .container {{ max-width: 1200px; margin: 0 auto; padding: 28px 24px; }}

  .kpi-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-bottom: 28px; }}
  .kpi {{ background: white; border-radius: 12px; padding: 22px 24px;
         box-shadow: 0 2px 10px rgba(0,0,0,0.08); text-align: center; }}
  .kpi .label {{ font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
                letter-spacing: 0.06em; color: #6b7280; margin-bottom: 10px; }}
  .kpi .value {{ font-size: 2.2rem; font-weight: 800; line-height: 1; }}
  .kpi .sub   {{ font-size: 0.82rem; color: #9ca3af; margin-top: 6px; }}
  .kpi.blue   {{ border-top: 4px solid #2E75B6; }} .kpi.blue .value {{ color: #2E75B6; }}
  .kpi.green  {{ border-top: 4px solid #1e8449; }} .kpi.green .value {{ color: #1e8449; }}
  .kpi.orange {{ border-top: 4px solid #d97706; }} .kpi.orange .value {{ color: #d97706; }}

  .section-title {{
    font-size: 1rem; font-weight: 700; color: #1F4E79;
    text-transform: uppercase; letter-spacing: 0.05em;
    border-left: 4px solid #2E75B6; padding-left: 10px;
    margin-bottom: 16px; margin-top: 28px;
  }}

  .charts-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }}
  .chart-card {{ background: white; border-radius: 12px; padding: 24px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
  .chart-card h3 {{ font-size: 0.9rem; font-weight: 700; color: #374151; margin-bottom: 16px; }}

  .table-card {{ background: white; border-radius: 12px; padding: 24px 28px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 28px; overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  thead th {{
    background: #1F4E79; color: white; padding: 10px 12px;
    text-align: left; font-weight: 600; white-space: nowrap;
  }}
  thead th:first-child {{ text-align: left; border-radius: 6px 0 0 0; }}
  thead th:last-child {{ border-radius: 0 6px 0 0; }}
  tbody tr:nth-child(even) {{ background: #f0f6fc; }}
  tbody tr:hover {{ background: #dbeafe; transition: background 0.15s; }}
  td {{ padding: 9px 12px; border-bottom: 1px solid #e5e7eb; }}
  td:first-child {{ font-weight: 600; color: #1F4E79; }}
  td.num {{ text-align: right; }}

  .footnote {{ font-size: 0.78rem; color: #9ca3af; line-height: 1.6;
              background: white; border-radius: 10px; padding: 16px 20px;
              box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-top: 28px; }}

  .info-box {{ background: #eff6ff; border-left: 4px solid #2E75B6; padding: 15px;
              border-radius: 6px; margin-bottom: 20px; font-size: 0.9rem; }}
  .info-box strong {{ color: #1F4E79; }}

  .action-items {{ background: white; border-radius: 12px; padding: 24px;
                  box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 28px; }}
  .action-items h3 {{ color: #1F4E79; margin-bottom: 15px; }}
  .action-items ol {{ margin-left: 20px; color: #666; }}
  .action-items li {{ margin-bottom: 10px; line-height: 1.6; }}

  @media (max-width: 768px) {{
    .kpi-grid {{ grid-template-columns: 1fr; }}
    .charts-row {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header>
  <h1>📊 Gmail Utility Analysis Report</h1>
  <p>Utility Company Identification Based on Email Activity</p>
</header>

<div class="container">

  <div class="info-box">
    📌 <strong>Report Generated:</strong> {timestamp} | <strong>Emails Analyzed:</strong> {total_emails}
  </div>

  <div class="kpi-grid">
    <div class="kpi blue">
      <div class="label">Total Emails Scanned</div>
      <div class="value">{total_emails}</div>
      <div class="sub">Messages analyzed</div>
    </div>
    <div class="kpi orange">
      <div class="label">Utility Emails Found</div>
      <div class="value">{utility_count}</div>
      <div class="sub">{email_percentage}% of total</div>
    </div>
    <div class="kpi green">
      <div class="label">Utilities Identified</div>
      <div class="value">{len(utilities)}</div>
      <div class="sub">Unique companies</div>
    </div>
  </div>

  <div class="section-title">📋 Companies Identified</div>

  <div class="table-card">
    <table>
      <thead>
        <tr>
          <th>Company</th>
          <th>Service Type</th>
          <th>Region</th>
          <th style="text-align: right;">Emails Found</th>
          <th>Latest Email</th>
        </tr>
      </thead>
      <tbody>
"""

        for company_name, info in sorted(
            utilities.items(), key=lambda x: x[1]['emails'], reverse=True
        ):
            html += f"""        <tr>
          <td><strong>{company_name}</strong></td>
          <td>{info['type']}</td>
          <td>{info['state']}</td>
          <td class="num">{info['emails']}</td>
          <td>{info['latest'][:10]}</td>
        </tr>
"""

        html += """      </tbody>
    </table>
  </div>

  <div class="action-items">
    <h3>✅ Next Steps</h3>
    <ol>
      <li><strong>Collect Your Bills:</strong> Gather 3-6 months of utility bills in PDF format</li>
      <li><strong>Organize by Company:</strong> Group bills by utility provider (Electric, Gas, Water, Internet)</li>
      <li><strong>Get Professional Analysis:</strong> Upload your bills for a detailed cost breakdown</li>
      <li><strong>Identify Savings:</strong> Discover optimization opportunities and potential savings</li>
      <li><strong>Take Action:</strong> Use recommendations to reduce your monthly expenses</li>
    </ol>
  </div>

  <div class="footnote">
    <strong>ℹ️ About This Report:</strong> This analysis scanned your Gmail for emails from known utility companies
    and identified which providers serve you. For detailed bill analysis with cost breakdowns, appliance-by-appliance
    estimates, and personalized savings recommendations, submit your utility PDFs using our
    <a href="https://mrjuandrful.typeform.com/to/Je0SD0aB" style="color: #2E75B6; font-weight: bold;">
    Utility Bill Analysis Form</a>. Analysis typically completed within 24 hours.
  </div>

</div>

</body>
</html>
"""
        return html

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
