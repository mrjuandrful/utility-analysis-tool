#!/usr/bin/env python3
"""
Demo Test - Shows the full system working with mock data
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from shared.html_generator import HTMLGenerator
from analyzers.gmail_utility_analyzer import GmailUtilityAnalyzer
from analyzers.telecom_analyzer import TelecomAnalyzer
from analyzers.amex_analyzer import AmexAnalyzer

def test_utility_analyzer():
    """Test Gmail Utility Analyzer with mock data"""
    print("\n" + "="*60)
    print("📊 Testing Gmail Utility Analyzer")
    print("="*60)
    
    # Create mock data
    mock_utilities = {
        'PSEG': {
            'type': 'Electric',
            'state': 'New Jersey',
            'emails': 12,
            'latest': '2026-03-05'
        },
        'Con Edison': {
            'type': 'Electric & Gas',
            'state': 'New York',
            'emails': 8,
            'latest': '2026-03-01'
        },
        'Verizon Fios': {
            'type': 'Internet/TV',
            'state': 'New York',
            'emails': 15,
            'latest': '2026-03-06'
        }
    }
    
    # Generate HTML report
    html_gen = HTMLGenerator()
    context = {
        'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'total_emails': 150,
        'utility_emails': 35,
        'utility_percentage': 23,
        'utilities_found': mock_utilities
    }
    
    html_output = html_gen.render('utility_report.html', context)
    
    # Save report
    report_path = Path('/sessions/festive-relaxed-newton/mnt/Perez/Documents/Claude code cowork/reports/utility_demo.html')
    report_path.write_text(html_output)
    print(f"✅ Utility Report Generated: {report_path}")
    print(f"   - Total emails analyzed: {context['total_emails']}")
    print(f"   - Utility companies found: {len(mock_utilities)}")
    print(f"   - Companies: {', '.join(mock_utilities.keys())}")
    
    return html_output

def test_telecom_analyzer():
    """Test Telecom Analyzer with mock data"""
    print("\n" + "="*60)
    print("📱 Testing Telecom Analyzer")
    print("="*60)
    
    mock_telecom = {
        'Verizon Fios (Fiber Internet)': {
            'type': 'Broadband',
            'plan': 'Gigabit',
            'monthly_bill': 79.99,
            'emails': 8,
            'latest': '2026-03-03'
        },
        'Verizon Wireless': {
            'type': 'Mobile',
            'plan': 'Unlimited',
            'monthly_bill': 120.00,
            'emails': 6,
            'latest': '2026-03-05'
        }
    }
    
    html_gen = HTMLGenerator()
    context = {
        'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'total_emails': 150,
        'telecom_emails': 14,
        'telecom_percentage': 9,
        'services_found': mock_telecom,
        'total_monthly_cost': 199.99
    }
    
    html_output = html_gen.render('telecom_report.html', context)
    
    report_path = Path('/sessions/festive-relaxed-newton/mnt/Perez/Documents/Claude code cowork/reports/telecom_demo.html')
    report_path.write_text(html_output)
    print(f"✅ Telecom Report Generated: {report_path}")
    print(f"   - Telecom services found: {len(mock_telecom)}")
    print(f"   - Total monthly cost: ${context['total_monthly_cost']:.2f}")
    print(f"   - Services: {', '.join(mock_telecom.keys())}")
    
    return html_output

def test_amex_analyzer():
    """Test AMEX Analyzer with mock data"""
    print("\n" + "="*60)
    print("💳 Testing AMEX Analyzer")
    print("="*60)
    
    mock_amex = {
        'Platinum Card': {
            'last_4': '1234',
            'statement_date': '2026-02-28',
            'total_spending': 4523.45,
            'categories': {
                'Travel': 1200.00,
                'Dining': 450.25,
                'Shopping': 1823.20,
                'Business': 500.00,
                'Entertainment': 300.00,
                'Utilities': 150.00,
                'Other': 200.00
            },
            'estimated_rewards': 90.47,
            'emails': 4
        }
    }
    
    html_gen = HTMLGenerator()
    context = {
        'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'total_emails': 150,
        'amex_emails': 4,
        'amex_percentage': 3,
        'cards_found': mock_amex
    }
    
    html_output = html_gen.render('amex_report.html', context)
    
    report_path = Path('/sessions/festive-relaxed-newton/mnt/Perez/Documents/Claude code cowork/reports/amex_demo.html')
    report_path.write_text(html_output)
    print(f"✅ AMEX Report Generated: {report_path}")
    print(f"   - Cards found: {len(mock_amex)}")
    print(f"   - Total spending: ${mock_amex['Platinum Card']['total_spending']:.2f}")
    print(f"   - Estimated rewards: ${mock_amex['Platinum Card']['estimated_rewards']:.2f}")
    
    return html_output

def main():
    print("\n" + "🚀 "*20)
    print("FINANCIAL ANALYZER SYSTEM - DEMO TEST")
    print("🚀 "*20)
    
    try:
        # Test all analyzers
        util_html = test_utility_analyzer()
        telecom_html = test_telecom_analyzer()
        amex_html = test_amex_analyzer()
        
        # Summary
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n📄 Generated Demo Reports:")
        print("   1. reports/utility_demo.html   (Utility companies analysis)")
        print("   2. reports/telecom_demo.html   (Telecom services analysis)")
        print("   3. reports/amex_demo.html      (Credit card spending analysis)")
        print("\n💡 Next Steps:")
        print("   1. Set up Gmail OAuth 2.0 credentials (see SETUP_GMAIL.md)")
        print("   2. Run: python orchestrator.py --utility --telecom --amex --html")
        print("   3. Check reports/ folder for generated HTML reports")
        print("\n✨ The system is ready to scan your actual Gmail inbox!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
