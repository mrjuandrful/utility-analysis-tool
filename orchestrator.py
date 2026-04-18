#!/usr/bin/env python3
"""
Financial Document Analyzer Orchestrator

Master CLI that coordinates all specialized analyzers (Utility, Telecom, AMEX)
to provide comprehensive financial analysis from Gmail.

Supports automatic email sending via Google Workspace CLI (gws).

Usage:
    python orchestrator.py                              # Run all analyzers
    python orchestrator.py --utility                    # Run only utility analyzer
    python orchestrator.py --utility --html             # Generate utility HTML report
    python orchestrator.py --utility --html --send-email # Generate & send email report
    python orchestrator.py --html                       # Generate all HTML reports
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import argparse
from pathlib import Path

from analyzers.gmail_utility_analyzer import GmailUtilityAnalyzer
from analyzers.telecom_analyzer import TelecomAnalyzer
from analyzers.amex_analyzer import AMEXAnalyzer
from analyzers.food_expense_analyzer import FoodExpenseAnalyzer
from email_sender import GWSEmailSender


class FinancialAnalyzerOrchestrator:
    """
    Orchestrates execution of multiple financial document analyzers.

    Coordinates:
    - GmailUtilityAnalyzer (electric, gas, internet companies)
    - TelecomAnalyzer (Verizon bills)
    - AMEXAnalyzer (credit card spending)

    Aggregates results into:
    - Combined JSON export
    - Master HTML dashboard
    - Summary report
    """

    def __init__(self, export_html: bool = False, export_json: bool = True):
        """
        Initialize the orchestrator.

        Args:
            export_html: Whether to generate HTML reports (default False)
            export_json: Whether to export JSON data (default True)
        """
        self.export_html = export_html
        self.export_json = export_json
        self.timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Analyzer instances
        self.analyzers = {
            'utility': GmailUtilityAnalyzer(),
            'telecom': TelecomAnalyzer(),
            'amex': AMEXAnalyzer(),
            'food': FoodExpenseAnalyzer(),
        }
        
        # Results storage
        self.results = {}
        self.aggregated_data = {}

    def run_all(self) -> Dict:
        """
        Run all analyzers sequentially.

        Returns:
            Dict with results from all analyzers
        """
        print("\n" + "="*60)
        print("🚀 Financial Document Analyzer Orchestrator")
        print("="*60)
        
        all_successful = True
        
        # Run each analyzer
        for analyzer_name, analyzer in self.analyzers.items():
            print(f"\n📊 Running {analyzer_name.upper()} Analyzer...")
            try:
                result = analyzer.run(
                    export_json=self.export_json,
                    export_html=self.export_html
                )
                self.results[analyzer_name] = result
                
                if result.get('success'):
                    print(f"✅ {analyzer_name.upper()} analysis complete")
                    if result.get('json_file'):
                        print(f"   JSON: {result['json_file']}")
                    if result.get('html_file'):
                        print(f"   HTML: {result['html_file']}")
                else:
                    print(f"⚠️  {analyzer_name.upper()} analysis failed: {result.get('error')}")
                    all_successful = False
                    
            except Exception as e:
                print(f"❌ {analyzer_name.upper()} error: {str(e)}")
                self.results[analyzer_name] = {
                    'success': False,
                    'error': str(e)
                }
                all_successful = False
        
        # Aggregate results
        print("\n" + "-"*60)
        print("📈 Aggregating Results...")
        self.aggregated_data = self._aggregate_results()
        
        # Export aggregated data
        if self.export_json:
            aggregate_file = self._export_aggregate_json()
            print(f"✅ Aggregated JSON: {aggregate_file}")
        
        if self.export_html:
            dashboard_file = self._generate_master_dashboard()
            print(f"✅ Master Dashboard: {dashboard_file}")
        
        print("="*60)
        if all_successful:
            print("✅ All analyses complete!")
        else:
            print("⚠️  Some analyses had errors. Review above for details.")
        print("="*60 + "\n")
        
        return {
            'success': all_successful,
            'results': self.results,
            'aggregated_data': self.aggregated_data,
            'timestamp': self.timestamp,
        }

    def run_specific(self, analyzer_names: List[str]) -> Dict:
        """
        Run specific analyzers only.

        Args:
            analyzer_names: List of analyzer names ('utility', 'telecom', 'amex')

        Returns:
            Dict with results from specified analyzers
        """
        print(f"\n🎯 Running {', '.join(analyzer_names).upper()} Analyzer(s)...\n")
        
        results = {}
        for name in analyzer_names:
            if name not in self.analyzers:
                print(f"❌ Unknown analyzer: {name}")
                continue
            
            analyzer = self.analyzers[name]
            result = analyzer.run(
                export_json=self.export_json,
                export_html=self.export_html
            )
            results[name] = result
            
            if result.get('success'):
                print(f"✅ {name.upper()} complete")
            else:
                print(f"❌ {name.upper()} failed: {result.get('error')}")
        
        return {'success': True, 'results': results}

    # ==================== AGGREGATION ====================

    def _aggregate_results(self) -> Dict:
        """
        Aggregate results from all analyzers.

        Returns:
            Dict with combined data from all analyzers
        """
        return {
            'timestamp': self.timestamp,
            'utility': self._extract_utility_data(),
            'telecom': self._extract_telecom_data(),
            'amex': self._extract_amex_data(),
            'food': self._extract_food_data(),
            'summary': self._generate_summary(),
        }

    def _extract_utility_data(self) -> Dict:
        """Extract and format utility analyzer results."""
        result = self.results.get('utility', {})
        if not result.get('success'):
            return {'error': 'Analysis failed'}
        
        parsed = result.get('parsed_data', {})
        return {
            'total_emails': self.analyzers['utility'].total_emails,
            'utility_emails': parsed.get('total_utility_emails', 0),
            'utilities_found': parsed.get('utilities_found', {}),
        }

    def _extract_telecom_data(self) -> Dict:
        """Extract and format telecom analyzer results."""
        result = self.results.get('telecom', {})
        if not result.get('success'):
            return {'error': 'Analysis failed'}
        
        parsed = result.get('parsed_data', {})
        return {
            'total_emails': self.analyzers['telecom'].total_emails,
            'bill_emails': parsed.get('total_bills', 0),
            'bills_found': parsed.get('bills_found', {}),
        }

    def _extract_amex_data(self) -> Dict:
        """Extract and format AMEX analyzer results."""
        result = self.results.get('amex', {})
        if not result.get('success'):
            return {'error': 'Analysis failed'}

        parsed = result.get('parsed_data', {})
        return {
            'total_emails': self.analyzers['amex'].total_emails,
            'statements': parsed.get('total_transactions', 0),
            'total_spending': parsed.get('total_spent', 0.0),
        }

    def _extract_food_data(self) -> Dict:
        """Extract and format food expense analyzer results."""
        result = self.results.get('food', {})
        if not result.get('success'):
            return {'error': 'Analysis failed'}

        parsed = result.get('parsed_data', {})
        return {
            'total_emails': self.analyzers['food'].total_emails,
            'receipt_emails': parsed.get('total_food_emails', 0),
            'total_spent': parsed.get('total_spent', 0.0),
            'by_vendor': parsed.get('by_vendor', {}),
            'expenses': parsed.get('expenses', []),
        }

    def _generate_summary(self) -> Dict:
        """
        Generate summary across all analyzers.

        Returns:
            Dict with summary statistics
        """
        return {
            'total_emails_analyzed': sum(
                self.analyzers[name].total_emails
                for name in self.analyzers
            ),
            'analysis_timestamp': self.timestamp,
            'analyzers_run': len([r for r in self.results.values() if r.get('success')]),
        }

    # ==================== EXPORTS ====================

    def _export_aggregate_json(self) -> str:
        """
        Export aggregated data as JSON.

        Returns:
            Path to exported JSON file
        """
        os.makedirs('reports', exist_ok=True)
        filepath = f'reports/aggregate_report_{self.timestamp}.json'
        
        with open(filepath, 'w') as f:
            json.dump(self.aggregated_data, f, indent=2, default=str)
        
        return filepath

    def _generate_master_dashboard(self) -> str:
        """
        Generate master HTML dashboard combining all reports.

        Returns:
            Path to generated HTML file
        """
        os.makedirs('reports', exist_ok=True)
        filepath = f'reports/master_dashboard_{self.timestamp}.html'
        
        html = self._build_dashboard_html()
        
        with open(filepath, 'w') as f:
            f.write(html)
        
        return filepath

    def _build_dashboard_html(self) -> str:
        """
        Build master dashboard HTML.

        Returns:
            HTML string
        """
        utility_data = self.aggregated_data.get('utility', {})
        telecom_data = self.aggregated_data.get('telecom', {})
        amex_data = self.aggregated_data.get('amex', {})
        food_data = self.aggregated_data.get('food', {})
        summary = self.aggregated_data.get('summary', {})

        food_vendor_rows = ''
        for vname, info in sorted(
            food_data.get('by_vendor', {}).items(),
            key=lambda x: x[1].get('total', 0), reverse=True
        ):
            food_vendor_rows += f"""
                <tr>
                  <td style="font-weight:600">{vname}</td>
                  <td>{info.get('category', '')}</td>
                  <td style="text-align:right">{info.get('count', 0)}</td>
                  <td style="text-align:right">${info.get('total', 0):,.2f}</td>
                  <td>{info.get('latest', '')}</td>
                </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Analysis Master Dashboard</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f0f4f8;
            color: #1a1a2e;
        }}
        header {{
            background: linear-gradient(135deg, #1F4E79 0%, #2E75B6 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 40px 24px; }}
        .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 40px; }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        .card h2 {{
            font-size: 1.1rem;
            margin-bottom: 20px;
            color: #1F4E79;
            border-bottom: 2px solid #2E75B6;
            padding-bottom: 10px;
        }}
        .card.food h2 {{
            color: #92400e;
            border-bottom-color: #f59e0b;
        }}
        .metric {{
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
        }}
        .metric-label {{ font-weight: 600; }}
        .metric-value {{ font-weight: bold; color: #2E75B6; }}
        .card.food .metric-value {{ color: #b45309; }}
        .food-section {{
            background: white;
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 40px;
        }}
        .food-section h2 {{
            font-size: 1.2rem;
            color: #92400e;
            border-bottom: 2px solid #f59e0b;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
        thead th {{
            background: #92400e; color: white; padding: 9px 12px;
            text-align: left; font-weight: 600;
        }}
        tbody tr:nth-child(even) {{ background: #fef3c7; }}
        tbody tr:hover {{ background: #fde68a; }}
        td {{ padding: 8px 12px; border-bottom: 1px solid #e5e7eb; }}
        .summary {{
            background: white;
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-top: 40px;
        }}
        .summary h2 {{
            font-size: 1.3rem;
            margin-bottom: 20px;
            color: #1F4E79;
        }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
        .summary-item {{
            text-align: center;
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
        }}
        .summary-item .value {{ font-size: 1.8rem; font-weight: bold; color: #2E75B6; }}
        .summary-item .label {{ font-size: 0.9rem; color: #666; margin-top: 5px; }}
        .timestamp {{ text-align: center; color: #999; font-size: 0.9rem; margin-top: 40px; }}
        @media (max-width: 1200px) {{
            .grid {{ grid-template-columns: repeat(2, 1fr); }}
            .summary-grid {{ grid-template-columns: 1fr; }}
        }}
        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>📊 Financial Analysis Master Dashboard</h1>
        <p>Comprehensive Overview of All Financial Documents</p>
    </header>

    <div class="container">
        <div class="grid">
            <div class="card">
                <h2>💰 Utility Companies</h2>
                <div class="metric">
                    <span class="metric-label">Utilities Found:</span>
                    <span class="metric-value">{len(utility_data.get('utilities_found', {}))}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Utility Emails:</span>
                    <span class="metric-value">{utility_data.get('utility_emails', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Scanned:</span>
                    <span class="metric-value">{utility_data.get('total_emails', 0)}</span>
                </div>
            </div>

            <div class="card">
                <h2>📱 Telecom Services</h2>
                <div class="metric">
                    <span class="metric-label">Services Found:</span>
                    <span class="metric-value">{len(telecom_data.get('bills_found', {}))}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Bill Emails:</span>
                    <span class="metric-value">{telecom_data.get('bill_emails', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Scanned:</span>
                    <span class="metric-value">{telecom_data.get('total_emails', 0)}</span>
                </div>
            </div>

            <div class="card">
                <h2>💳 Credit Card</h2>
                <div class="metric">
                    <span class="metric-label">Statements Found:</span>
                    <span class="metric-value">{amex_data.get('statements', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Spending:</span>
                    <span class="metric-value">${{amex_data.get('total_spending', 0):,.2f}}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Scanned:</span>
                    <span class="metric-value">{amex_data.get('total_emails', 0)}</span>
                </div>
            </div>

            <div class="card food">
                <h2>🍗 Food Expenses</h2>
                <div class="metric">
                    <span class="metric-label">Receipts Found:</span>
                    <span class="metric-value">{food_data.get('receipt_emails', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Spent:</span>
                    <span class="metric-value">${{food_data.get('total_spent', 0):,.2f}}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Vendors Found:</span>
                    <span class="metric-value">{len(food_data.get('by_vendor', {}))}</span>
                </div>
            </div>
        </div>

        <div class="food-section">
            <h2>🍗 Food Expenses — By Vendor</h2>
            <table>
                <thead>
                    <tr>
                        <th>Vendor</th>
                        <th>Category</th>
                        <th style="text-align:right">Orders</th>
                        <th style="text-align:right">Total Spent</th>
                        <th>Latest Order</th>
                    </tr>
                </thead>
                <tbody>
                    {food_vendor_rows if food_vendor_rows else '<tr><td colspan="5" style="text-align:center;color:#9ca3af">No food receipts found</td></tr>'}
                </tbody>
            </table>
        </div>

        <div class="summary">
            <h2>📈 Analysis Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="value">{summary.get('total_emails_analyzed', 0)}</div>
                    <div class="label">Total Emails Analyzed</div>
                </div>
                <div class="summary-item">
                    <div class="value">{summary.get('analyzers_run', 0)}/4</div>
                    <div class="label">Analyzers Executed</div>
                </div>
                <div class="summary-item">
                    <div class="value">{summary.get('analysis_timestamp', 'N/A')}</div>
                    <div class="label">Analysis Time</div>
                </div>
            </div>
        </div>

        <div class="timestamp">
            Generated: {self.timestamp}
        </div>
    </div>
</body>
</html>
"""
        return html

    def send_utility_report_email(self, recipients: Optional[List[str]] = None) -> dict:
        """
        Send utility + food expense report via email using gws.

        Sends the master dashboard HTML (which now includes food expenses).
        Recipients default to Juan (mrjuandrful@gmail.com) and Melissa (mkperez1027@gmail.com).

        Args:
            recipients: List of email addresses to send to

        Returns:
            Dict with send status
        """
        if not self.export_html:
            print("⚠️  HTML export disabled. Enable with --html to send emails.")
            return {'success': False, 'error': 'HTML export required'}

        try:
            # Prefer master dashboard which now contains food expenses
            dashboard_html = self._build_dashboard_html()

            # Send email
            sender = GWSEmailSender()
            result = sender.send_utility_report(
                html_content=dashboard_html,
                recipients=recipients,
                month=datetime.now().strftime("%B %Y")
            )

            if result.get('success'):
                print(f"✅ Report email prepared for sending")
                print(f"   Recipients: {', '.join(result.get('to', []))}")
                print(f"   Subject: {result.get('subject')}")
            else:
                print(f"❌ Failed to prepare email: {result.get('error')}")

            return result

        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return {'success': False, 'error': str(e)}

    def list_analyzers(self):
        """Print available analyzers and their info."""
        print("\n" + "="*60)
        print("Available Analyzers:")
        print("="*60)

        for name, analyzer in self.analyzers.items():
            metadata = analyzer.get_metadata()
            print(f"\n📊 {metadata['name']}")
            print(f"   Type: {metadata['domain']}")
            print(f"   Description: {metadata['description']}")
            print(f"   Supports: {', '.join(metadata.get('supports', []))}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Financial Document Analyzer Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator.py                 # Run all analyzers
  python orchestrator.py --utility       # Run only utility analyzer
  python orchestrator.py --html          # Generate HTML reports
  python orchestrator.py --list          # Show available analyzers
        """
    )
    
    parser.add_argument(
        '--utility',
        action='store_true',
        help='Run utility analyzer only'
    )
    parser.add_argument(
        '--telecom',
        action='store_true',
        help='Run telecom analyzer only'
    )
    parser.add_argument(
        '--amex',
        action='store_true',
        help='Run AMEX analyzer only'
    )
    parser.add_argument(
        '--food',
        action='store_true',
        help='Run food expense analyzer only'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML reports'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        default=True,
        help='Export JSON data (default)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available analyzers'
    )
    parser.add_argument(
        '--send-email',
        action='store_true',
        help='Send utility + food expense report via email to Juan & Melissa'
    )

    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = FinancialAnalyzerOrchestrator(
        export_html=args.html,
        export_json=args.json
    )
    
    # Handle list command
    if args.list:
        orchestrator.list_analyzers()
        return
    
    # Determine which analyzers to run
    selected = []
    if args.utility:
        selected.append('utility')
    if args.telecom:
        selected.append('telecom')
    if args.amex:
        selected.append('amex')
    if args.food:
        selected.append('food')
    
    # Run analyzers
    if selected:
        orchestrator.run_specific(selected)
    else:
        orchestrator.run_all()

    # Send email if requested
    if args.send_email:
        print("\n" + "="*60)
        print("📧 Email Sending")
        print("="*60)
        orchestrator.send_utility_report_email()


if __name__ == '__main__':
    main()
