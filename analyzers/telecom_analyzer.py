#!/usr/bin/env python3
"""
Telecom Analyzer - Verizon Bills

Inherits from BaseAnalyzer to search Gmail for Verizon bills
(both Fios and Wireless) and parse them into structured data.

Supports:
  - Verizon Fios (Home Internet + Phone) - Bill code: 867-0001
  - Verizon Wireless (Mobile) - Bill code: 7065-00001
"""

import re
from typing import Dict, List
from analyzers.base_analyzer import BaseAnalyzer


# Verizon bill patterns and metadata
VERIZON_BILL_TYPES = {
    'fios': {
        'name': 'Verizon Fios',
        'type': 'Internet/TV/Phone',
        'bill_codes': ['867-0001'],
        'keywords': ['fios', 'internet', 'broadband'],
        'state': 'National',
    },
    'wireless': {
        'name': 'Verizon Wireless',
        'type': 'Mobile/Data',
        'bill_codes': ['7065-00001'],
        'keywords': ['wireless', 'mobile', 'account balance'],
        'state': 'National',
    },
}


class TelecomAnalyzer(BaseAnalyzer):
    """
    Analyzer for Verizon telecom bills from Gmail.

    Searches for emails from Verizon containing bills/statements,
    then extracts key information:
    - Bill type (Fios vs Wireless)
    - Amount due
    - Due date
    - Service dates
    - Account number
    """

    def __init__(self, service=None):
        """Initialize the telecom analyzer."""
        super().__init__(service=service)
        self.analyzer_type = 'telecom'
        self.bills_found = {}
        self.total_bills = 0

    # ==================== DOMAIN-SPECIFIC: SEARCH ====================

    def search_emails(self) -> List[Dict]:
        """
        Search Gmail for Verizon bill emails.

        Searches for emails from Verizon containing 'bill', 'statement',
        or 'invoice' keywords.

        Returns:
            List of email metadata dicts
        """
        # Search for Verizon emails with bill-related keywords
        query = 'from:verizon subject:(bill OR statement OR invoice)'
        return self.search_emails_generic(query=query, max_results=10)

    # ==================== DOMAIN-SPECIFIC: PARSE ====================

    def parse_documents(self, emails: List[Dict]) -> Dict:
        """
        Parse Verizon bill emails to extract key information.

        Extracts:
        - Bill type (Fios or Wireless)
        - Amount due
        - Due date
        - Service date range
        - Account number
        - Email details

        Returns:
            Dict with bills_found, total_bills, bill_details
        """
        bills = {}
        bill_details = []
        bill_count = 0

        for email in emails:
            from_addr = email.get('from', '')
            subject = email.get('subject', '')
            date = email.get('date', '')
            email_id = email.get('id', '')

            # Check if this is a Verizon bill
            if self._is_verizon_bill(from_addr, subject):
                bill_count += 1

                # Determine which Verizon service this is
                bill_type = self._identify_bill_type(from_addr, subject)

                # Extract structured data from email
                extracted = {
                    'from': from_addr,
                    'subject': subject,
                    'date': date,
                    'id': email_id,
                    'bill_type': bill_type,
                    'service': VERIZON_BILL_TYPES.get(bill_type, {}).get('name', 'Unknown'),
                }

                # Try to extract amount due (pattern: $XX.XX)
                amount = self._extract_amount(subject)
                if amount:
                    extracted['amount_due'] = amount

                # Store details
                bill_details.append(extracted)

                # Accumulate bill type counts
                service_name = extracted['service']
                if service_name not in bills:
                    bills[service_name] = {
                        'type': VERIZON_BILL_TYPES.get(bill_type, {}).get('type', 'Unknown'),
                        'bills': 0,
                        'latest': date,
                    }
                bills[service_name]['bills'] += 1

        self.bills_found = bills
        self.total_bills = bill_count

        return {
            'bills_found': bills,
            'total_bills': bill_count,
            'bill_details': bill_details,
        }

    # ==================== HELPER METHODS ====================

    def _is_verizon_bill(self, from_addr: str, subject: str) -> bool:
        """
        Check if an email is from Verizon and mentions bills.

        Args:
            from_addr: Email sender address
            subject: Email subject line

        Returns:
            True if email is from Verizon and mentions bills
        """
        email_text = (from_addr + ' ' + subject).lower()

        # Must contain 'verizon'
        if 'verizon' not in email_text:
            return False

        # Must mention bills/statements
        bill_keywords = ['bill', 'statement', 'invoice', 'account']
        if not any(keyword in email_text for keyword in bill_keywords):
            return False

        return True

    def _identify_bill_type(self, from_addr: str, subject: str) -> str:
        """
        Determine if this is a Fios or Wireless bill.

        Args:
            from_addr: Email sender address
            subject: Email subject line

        Returns:
            'fios', 'wireless', or 'unknown'
        """
        email_text = (from_addr + ' ' + subject).lower()

        # Check for Fios indicators
        fios_keywords = ['fios', 'internet', 'broadband', 'tv service']
        if any(keyword in email_text for keyword in fios_keywords):
            return 'fios'

        # Check for Wireless indicators
        wireless_keywords = ['wireless', 'mobile', 'plan', 'line']
        if any(keyword in email_text for keyword in wireless_keywords):
            return 'wireless'

        # Default to unknown
        return 'unknown'

    def _extract_amount(self, text: str) -> str:
        """
        Extract dollar amount from text.

        Args:
            text: Text to search for amounts (e.g., "$123.45")

        Returns:
            Dollar amount string or None
        """
        # Pattern: $XXX.XX
        match = re.search(r'\$[\d,]+\.\d{2}', text)
        if match:
            return match.group(0)
        return None

    def generate_html_report(self, data: Dict) -> str:
        """
        Generate an HTML report from parsed Verizon bill data.

        Args:
            data: Dict with bills_found, total_bills, etc.

        Returns:
            HTML string ready to write to file
        """
        bills = data.get('bills_found', {})
        timestamp = self.get_timestamp()
        total_emails = self.total_emails
        bill_count = data.get('total_bills', 0)

        # Calculate percentage
        email_percentage = round(
            (bill_count / max(total_emails, 1)) * 100, 1
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Verizon Bill Analysis Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f4f8; color: #1a1a2e; }}

  header {{
    background: linear-gradient(135deg, #C81828 0%, #EB3B23 100%);
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
  .kpi.red    {{ border-top: 4px solid #EB3B23; }} .kpi.red .value {{ color: #EB3B23; }}
  .kpi.green  {{ border-top: 4px solid #1e8449; }} .kpi.green .value {{ color: #1e8449; }}
  .kpi.orange {{ border-top: 4px solid #d97706; }} .kpi.orange .value {{ color: #d97706; }}

  .section-title {{
    font-size: 1rem; font-weight: 700; color: #C81828;
    text-transform: uppercase; letter-spacing: 0.05em;
    border-left: 4px solid #EB3B23; padding-left: 10px;
    margin-bottom: 16px; margin-top: 28px;
  }}

  .table-card {{ background: white; border-radius: 12px; padding: 24px 28px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 28px; overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  thead th {{
    background: #C81828; color: white; padding: 10px 12px;
    text-align: left; font-weight: 600; white-space: nowrap;
  }}
  tbody tr:nth-child(even) {{ background: #f0f6fc; }}
  tbody tr:hover {{ background: #ffeeee; transition: background 0.15s; }}
  td {{ padding: 9px 12px; border-bottom: 1px solid #e5e7eb; }}
  td:first-child {{ font-weight: 600; color: #C81828; }}

  .info-box {{ background: #fff3f3; border-left: 4px solid #EB3B23; padding: 15px;
              border-radius: 6px; margin-bottom: 20px; font-size: 0.9rem; }}
  .info-box strong {{ color: #C81828; }}

  .footnote {{ font-size: 0.78rem; color: #9ca3af; line-height: 1.6;
              background: white; border-radius: 10px; padding: 16px 20px;
              box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-top: 28px; }}

  @media (max-width: 768px) {{
    .kpi-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header>
  <h1>📱 Verizon Bill Analysis Report</h1>
  <p>Telecom Service Bills Identified From Email Activity</p>
</header>

<div class="container">

  <div class="info-box">
    📌 <strong>Report Generated:</strong> {timestamp} | <strong>Emails Analyzed:</strong> {total_emails}
  </div>

  <div class="kpi-grid">
    <div class="kpi red">
      <div class="label">Total Emails Scanned</div>
      <div class="value">{total_emails}</div>
      <div class="sub">Messages analyzed</div>
    </div>
    <div class="kpi orange">
      <div class="label">Bill Emails Found</div>
      <div class="value">{bill_count}</div>
      <div class="sub">{email_percentage}% of total</div>
    </div>
    <div class="kpi green">
      <div class="label">Services Identified</div>
      <div class="value">{len(bills)}</div>
      <div class="sub">Unique services</div>
    </div>
  </div>

  <div class="section-title">📊 Services Identified</div>

  <div class="table-card">
    <table>
      <thead>
        <tr>
          <th>Service</th>
          <th>Type</th>
          <th style="text-align: right;">Bills Found</th>
          <th>Latest Bill</th>
        </tr>
      </thead>
      <tbody>
"""

        for service_name, info in sorted(
            bills.items(), key=lambda x: x[1]['bills'], reverse=True
        ):
            html += f"""        <tr>
          <td><strong>{service_name}</strong></td>
          <td>{info['type']}</td>
          <td style="text-align: right;">{info['bills']}</td>
          <td>{info['latest'][:10]}</td>
        </tr>
"""

        html += """      </tbody>
    </table>
  </div>

  <div class="footnote">
    <strong>ℹ️ About This Report:</strong> This analysis scanned your Gmail for emails from Verizon
    and identified which telecom services you use (Fios or Wireless). For detailed bill analysis with usage breakdown,
    cost optimization, and plan recommendations, submit your Verizon bills using our
    <a href="https://mrjuandrful.typeform.com/to/Je0SD0aB" style="color: #C81828; font-weight: bold;">
    Telecom Bill Analysis Form</a>. Analysis typically completed within 24 hours.
  </div>

</div>

</body>
</html>
"""
        return html

    def run(self, export_json: bool = True, export_html: bool = False) -> Dict:
        """
        Run the complete telecom analysis pipeline.

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
            html_file = f'reports/telecom_report_{self.run_timestamp}.html'

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
            Dict with name, description, version, supported services
        """
        return {
            'name': 'Verizon Telecom Analyzer',
            'description': 'Identifies and analyzes Verizon bills from Gmail',
            'version': '1.0',
            'domain': 'telecom',
            'analyzer_type': 'telecom',
            'supports': ['Verizon Fios', 'Verizon Wireless']
        }


def main():
    """CLI entry point for backwards compatibility."""
    analyzer = TelecomAnalyzer()
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
