#!/usr/bin/env python3
"""
Gmail Utility Analyzer
Analyzes Gmail for utility company emails and generates a comprehensive report.
Looks up utility company information and creates an HTML report similar to other analysis tools.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core import retry
import googleapiclient.discovery

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Utility company patterns and info
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

class GmailUtilityAnalyzer:
    def __init__(self):
        self.service = None
        self.utilities_found = []
        self.total_emails = 0
        self.utility_emails = 0
        self.email_details = []  # Store detailed email info

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Check for stored credentials
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
        return self.service

    def search_utility_emails(self, query: str = 'bill OR statement OR invoice') -> List[Dict]:
        """Search Gmail for utility-related emails"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            self.total_emails = len(messages)

            utility_messages = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                headers = msg['payload']['headers']
                email_from = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                email_subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                email_date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

                # Check if this is a utility email
                if self._is_utility_email(email_from, email_subject):
                    self.utility_emails += 1
                    utility_messages.append({
                        'from': email_from,
                        'subject': email_subject,
                        'date': email_date,
                        'id': message['id']
                    })

            return utility_messages
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []

    def _is_utility_email(self, email_from: str, subject: str) -> bool:
        """Check if email is from a utility company"""
        email_lower = email_from.lower() + ' ' + subject.lower()

        for company_key in UTILITY_COMPANIES.keys():
            if company_key in email_lower:
                return True
        return False

    def identify_utilities(self, messages: List[Dict]) -> Dict:
        """Identify utilities from messages"""
        utilities = {}

        for message in messages:
            email_text = (message['from'] + ' ' + message['subject']).lower()

            for company_key, company_info in UTILITY_COMPANIES.items():
                if company_key in email_text:
                    company_name = company_info['name']
                    if company_name not in utilities:
                        utilities[company_name] = {
                            'type': company_info['type'],
                            'state': company_info['state'],
                            'emails': 0,
                            'latest': message['date']
                        }
                    utilities[company_name]['emails'] += 1

        return utilities

    def generate_html_report(self, utilities: Dict) -> str:
        """Generate HTML report similar to other analysis tools"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calculate email distribution percentage
        total_utility_emails = sum(u['emails'] for u in utilities.values())
        email_percentage = round((total_utility_emails / max(self.total_emails, 1)) * 100, 1)

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
    📌 <strong>Report Generated:</strong> {timestamp} | <strong>Emails Analyzed:</strong> {self.total_emails}
  </div>

  <div class="kpi-grid">
    <div class="kpi blue">
      <div class="label">Total Emails Scanned</div>
      <div class="value">{self.total_emails}</div>
      <div class="sub">Messages analyzed</div>
    </div>
    <div class="kpi orange">
      <div class="label">Utility Emails Found</div>
      <div class="value">{self.utility_emails}</div>
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

        for company_name, info in sorted(utilities.items(), key=lambda x: x[1]['emails'], reverse=True):
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

    def run_analysis(self) -> str:
        """Run complete analysis and return HTML report"""
        print("Authenticating with Gmail...")
        self.authenticate()

        print("Searching for utility emails...")
        messages = self.search_utility_emails()

        print(f"Found {len(messages)} utility emails")
        utilities = self.identify_utilities(messages)

        print(f"Identified {len(utilities)} utility companies")
        html_report = self.generate_html_report(utilities)

        return html_report


def main():
    """Main execution"""
    analyzer = GmailUtilityAnalyzer()
    html_report = analyzer.run_analysis()

    # Save report
    output_file = 'Gmail_Utility_Analysis_Report.html'
    with open(output_file, 'w') as f:
        f.write(html_report)

    print(f"\n✅ Report generated: {output_file}")


if __name__ == '__main__':
    main()
