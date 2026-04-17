#!/usr/bin/env python3
"""
Food Expense Analyzer

Searches Gmail for food-related receipt emails (Chick-fil-A, Dave's Hot Chicken,
and other restaurants/delivery services) and extracts expense data.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional

from analyzers.base_analyzer import BaseAnalyzer


FOOD_VENDORS = {
    'chick-fil-a': {
        'name': "Chick-fil-A",
        'category': 'Fast Food',
        'keywords': ['chick-fil-a', 'chickfila', 'chick fil a'],
        'email_domains': ['chick-fil-a.com', 'chickfila.com'],
    },
    'daves-hot-chicken': {
        'name': "Dave's Hot Chicken",
        'category': 'Fast Food',
        'keywords': ["dave's hot chicken", 'daveshotchicken', 'daves hot chicken'],
        'email_domains': ['daveshotchicken.com'],
    },
    'doordash': {
        'name': 'DoorDash',
        'category': 'Delivery',
        'keywords': ['doordash'],
        'email_domains': ['doordash.com'],
    },
    'uber-eats': {
        'name': 'Uber Eats',
        'category': 'Delivery',
        'keywords': ['uber eats', 'ubereats'],
        'email_domains': ['uber.com', 'ubereats.com'],
    },
    'grubhub': {
        'name': 'Grubhub',
        'category': 'Delivery',
        'keywords': ['grubhub'],
        'email_domains': ['grubhub.com'],
    },
    'instacart': {
        'name': 'Instacart',
        'category': 'Grocery Delivery',
        'keywords': ['instacart'],
        'email_domains': ['instacart.com'],
    },
}

FOOD_SEARCH_SUBJECTS = ['receipt', 'order confirmation', 'your order', 'thank you for your order']


class FoodExpenseAnalyzer(BaseAnalyzer):
    """
    Analyzer for food receipt emails from Gmail.

    Searches for Chick-fil-A, Dave's Hot Chicken, and other restaurant/
    delivery receipts, extracting vendor, amount, and date.
    """

    def __init__(self):
        super().__init__(analyzer_name='FoodExpenseAnalyzer')
        self.analyzer_type = 'food_expenses'
        self.total_emails = 0
        self.run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.expenses_found = []
        self.total_food_spending = 0.0

    # ==================== DOMAIN-SPECIFIC: SEARCH ====================

    def search_emails(self) -> List[Dict]:
        """
        Search Gmail for food receipt emails.

        Covers Chick-fil-A, Dave's Hot Chicken, and major delivery platforms.
        """
        vendor_terms = ' OR '.join([
            '"chick-fil-a"', '"chick fil a"', '"chickfila"',
            '"dave\'s hot chicken"', '"daveshotchicken"',
            'doordash', 'grubhub', '"uber eats"', 'instacart',
        ])
        subject_terms = 'receipt OR "order confirmation" OR "your order" OR "thank you for your order"'
        query = f'({vendor_terms}) ({subject_terms})'
        results = self.search_emails_generic(query=query, max_results=25)
        self.total_emails = len(results)
        return results

    # ==================== DOMAIN-SPECIFIC: PARSE ====================

    def parse_documents(self, emails: List[Dict]) -> Dict:
        """
        Parse food receipt emails to extract vendor, date, and amount.

        Returns structured expense data grouped by vendor.
        """
        expenses = []
        total_spent = 0.0
        by_vendor: Dict[str, Dict] = {}

        for email in emails:
            headers = email.get('payload', {}).get('headers', [])
            from_addr = self._get_header(headers, 'From') or ''
            subject = self._get_header(headers, 'Subject') or ''
            date_raw = self._get_header(headers, 'Date') or ''
            email_id = email.get('id', '')

            vendor_info = self._identify_vendor(from_addr, subject)
            if not vendor_info:
                continue

            amount = self._extract_amount(subject + ' ' + email.get('snippet', ''))
            parsed_date = self._parse_date(date_raw)

            expense = {
                'id': email_id,
                'vendor': vendor_info['name'],
                'category': vendor_info['category'],
                'date': parsed_date,
                'amount': amount,
                'subject': subject,
                'from': from_addr,
            }
            expenses.append(expense)

            if amount:
                total_spent += amount

            vname = vendor_info['name']
            if vname not in by_vendor:
                by_vendor[vname] = {
                    'category': vendor_info['category'],
                    'count': 0,
                    'total': 0.0,
                    'latest': parsed_date,
                }
            by_vendor[vname]['count'] += 1
            if amount:
                by_vendor[vname]['total'] += amount
            if parsed_date and (not by_vendor[vname]['latest'] or parsed_date > by_vendor[vname]['latest']):
                by_vendor[vname]['latest'] = parsed_date

        self.expenses_found = expenses
        self.total_food_spending = total_spent

        return {
            'expenses': expenses,
            'by_vendor': by_vendor,
            'total_food_emails': len(expenses),
            'total_spent': total_spent,
        }

    # ==================== HELPER METHODS ====================

    def _get_header(self, headers: List[Dict], name: str) -> Optional[str]:
        for h in headers:
            if h.get('name', '').lower() == name.lower():
                return h.get('value', '')
        return None

    def _identify_vendor(self, from_addr: str, subject: str) -> Optional[Dict]:
        text = (from_addr + ' ' + subject).lower()
        for vendor_key, vendor in FOOD_VENDORS.items():
            for kw in vendor['keywords']:
                if kw in text:
                    return vendor
            for domain in vendor['email_domains']:
                if domain in text:
                    return vendor
        return None

    def _extract_amount(self, text: str) -> Optional[float]:
        match = re.search(r'\$[\d,]+\.\d{2}', text)
        if match:
            try:
                return float(match.group(0).replace('$', '').replace(',', ''))
            except ValueError:
                pass
        return None

    def _parse_date(self, date_str: str) -> str:
        for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S']:
            try:
                return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        return date_str[:10] if date_str else ''

    def generate_html_report(self, data: Dict) -> str:
        """Generate an inline HTML report for food expenses."""
        by_vendor = data.get('by_vendor', {})
        expenses = data.get('expenses', [])
        total_spent = data.get('total_spent', 0.0)
        total_emails = data.get('total_food_emails', 0)

        vendor_rows = ''
        for vname, info in sorted(by_vendor.items(), key=lambda x: x[1]['total'], reverse=True):
            vendor_rows += f"""
        <tr>
          <td><strong>{vname}</strong></td>
          <td>{info['category']}</td>
          <td class="num">{info['count']}</td>
          <td class="num">${info['total']:,.2f}</td>
          <td>{info.get('latest', '')}</td>
        </tr>"""

        expense_rows = ''
        for exp in sorted(expenses, key=lambda x: x.get('date', ''), reverse=True):
            amt = f"${exp['amount']:,.2f}" if exp['amount'] else 'N/A'
            expense_rows += f"""
        <tr>
          <td>{exp.get('date', '')}</td>
          <td><strong>{exp.get('vendor', '')}</strong></td>
          <td>{exp.get('subject', '')[:60]}</td>
          <td class="num">{amt}</td>
        </tr>"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Food Expenses Report</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f9fafb; color: #111827; }}
    header {{ background: linear-gradient(135deg, #b45309 0%, #f59e0b 100%); color: white; padding: 36px; text-align: center; }}
    header h1 {{ font-size: 2rem; margin-bottom: 8px; }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }}
    .kpi {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); text-align: center; }}
    .kpi .label {{ font-size: 0.78rem; font-weight: 600; text-transform: uppercase; color: #6b7280; margin-bottom: 8px; }}
    .kpi .value {{ font-size: 2rem; font-weight: 800; color: #b45309; }}
    .section-title {{ font-size: 0.95rem; font-weight: 700; color: #92400e; text-transform: uppercase; letter-spacing: 0.05em; border-left: 4px solid #f59e0b; padding-left: 10px; margin: 24px 0 14px; }}
    .table-card {{ background: white; border-radius: 10px; padding: 22px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); margin-bottom: 24px; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.87rem; }}
    thead th {{ background: #92400e; color: white; padding: 10px 12px; text-align: left; font-weight: 600; }}
    tbody tr:nth-child(even) {{ background: #fef3c7; }}
    tbody tr:hover {{ background: #fde68a; transition: background 0.15s; }}
    td {{ padding: 9px 12px; border-bottom: 1px solid #e5e7eb; }}
    td.num {{ text-align: right; }}
    .timestamp {{ text-align: center; color: #9ca3af; font-size: 0.85rem; margin-top: 32px; }}
  </style>
</head>
<body>
<header>
  <h1>🍗 Food Expense Report</h1>
  <p>Gmail Receipt Analysis — Chick-fil-A, Dave's Hot Chicken & More</p>
</header>
<div class="container">
  <div class="kpi-grid">
    <div class="kpi">
      <div class="label">Total Scanned</div>
      <div class="value">{self.total_emails}</div>
    </div>
    <div class="kpi">
      <div class="label">Food Receipts Found</div>
      <div class="value">{total_emails}</div>
    </div>
    <div class="kpi">
      <div class="label">Total Spent</div>
      <div class="value">${total_spent:,.2f}</div>
    </div>
  </div>

  <div class="section-title">By Vendor</div>
  <div class="table-card">
    <table>
      <thead>
        <tr><th>Vendor</th><th>Category</th><th>Orders</th><th>Total Spent</th><th>Latest Order</th></tr>
      </thead>
      <tbody>{vendor_rows}</tbody>
    </table>
  </div>

  <div class="section-title">All Receipts</div>
  <div class="table-card">
    <table>
      <thead>
        <tr><th>Date</th><th>Vendor</th><th>Subject</th><th>Amount</th></tr>
      </thead>
      <tbody>{expense_rows}</tbody>
    </table>
  </div>

  <div class="timestamp">Generated: {self.run_timestamp}</div>
</div>
</body>
</html>"""

    # ==================== PIPELINE ====================

    def run(self, export_json: bool = True, export_html: bool = False) -> Dict:
        """
        Run the full food expense analysis pipeline.

        Returns:
            Dict with 'success', 'parsed_data', 'json_file', 'html_file'
        """
        try:
            self.run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            print(f"\n{'='*60}")
            print("Starting FoodExpenseAnalyzer")
            print(f"{'='*60}")

            print("\n→ Searching for food receipt emails...")
            emails = self.search_emails()

            if not emails:
                print("⚠  No food receipt emails found")
                return {
                    'success': True,
                    'parsed_data': {
                        'expenses': [],
                        'by_vendor': {},
                        'total_food_emails': 0,
                        'total_spent': 0.0,
                    },
                    'json_file': None,
                    'html_file': None,
                }

            print("\n→ Parsing food receipts...")
            parsed_data = self.parse_documents(emails)
            print(f"✓ Found {parsed_data['total_food_emails']} food receipts totalling ${parsed_data['total_spent']:,.2f}")

            json_file = None
            if export_json:
                os.makedirs('data', exist_ok=True)
                json_file = f'data/food_expenses_{self.run_timestamp}.json'
                with open(json_file, 'w') as f:
                    json.dump(parsed_data, f, indent=2, default=str)
                print(f"✓ Exported JSON: {json_file}")

            html_file = None
            if export_html:
                os.makedirs('reports', exist_ok=True)
                html_file = f'reports/food_expenses_{self.run_timestamp}.html'
                html = self.generate_html_report(parsed_data)
                with open(html_file, 'w') as f:
                    f.write(html)
                print(f"✓ Generated HTML: {html_file}")

            return {
                'success': True,
                'parsed_data': parsed_data,
                'json_file': json_file,
                'html_file': html_file,
            }

        except Exception as e:
            print(f"✗ FoodExpenseAnalyzer error: {e}")
            return {'success': False, 'error': str(e)}

    def get_timestamp(self) -> str:
        return self.run_timestamp

    @classmethod
    def get_metadata(cls) -> Dict:
        return {
            'name': 'Food Expense Analyzer',
            'description': "Scrapes Gmail for food receipts: Chick-fil-A, Dave's Hot Chicken, delivery apps",
            'version': '1.0',
            'domain': 'food_expenses',
            'analyzer_type': 'food',
            'supports': ["Chick-fil-A", "Dave's Hot Chicken", 'DoorDash', 'Uber Eats', 'Grubhub', 'Instacart'],
        }


def main():
    analyzer = FoodExpenseAnalyzer()
    result = analyzer.run(export_json=True, export_html=True)
    if result.get('success'):
        print("✅ Food expense analysis complete!")
        if result.get('json_file'):
            print(f"   JSON: {result['json_file']}")
        if result.get('html_file'):
            print(f"   HTML: {result['html_file']}")
    else:
        print(f"❌ Analysis failed: {result.get('error')}")


if __name__ == '__main__':
    main()
