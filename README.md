# Financial Document Analyzer Platform 📊

A comprehensive multi-analyzer platform that automatically detects and analyzes financial documents from Gmail, including utilities, telecom bills, and credit card statements.

## 🎯 What It Does

Automatically analyzes your Gmail inbox to identify and categorize:

- **💰 Utility Companies** - PSEG, Con Edison, Eversource, National Grid, etc.
- **📱 Telecom Services** - Verizon Fios & Wireless bills
- **💳 Credit Card Spending** - American Express statements with category breakdown

Generates professional HTML reports + JSON exports + master dashboard.

## 🚀 Current Status

**Week 1-5: Core Platform Complete!**
- ✅ BaseAnalyzer abstract framework
- ✅ OAuth 2.0 authentication (AuthManager)
- ✅ Email/HTML parsing utilities
- ✅ 3 complete domain-specific analyzers
- ✅ Jinja2 template system for HTML reports
- ✅ Master orchestrator CLI
- ✅ 298 unit + integration tests
- ✅ Comprehensive documentation

**Ready for:**
- Production deployment
- Customer intake automation (Typeform)
- Report generation service
- Business model integration

## 🏗️ System Architecture

**Master CLI → Orchestrator → 3 Domain-Specific Analyzers**

```
orchestrator.py (Master)
├── GmailUtilityAnalyzer      (Utilities)
├── TelecomAnalyzer           (Verizon)
└── AMEXAnalyzer              (Credit Cards)

All analyzers:
├── Inherit from BaseAnalyzer
├── Use shared AuthManager
├── Render via HTMLGenerator
└── Generate Jinja2 templates
```

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for complete system documentation.

## 📁 Project Structure

```
utility-analysis-tool/
├── orchestrator.py            # Master CLI (450 lines)
│
├── analyzers/
│   ├── base_analyzer.py       # Abstract base (290 lines)
│   ├── gmail_utility_analyzer.py  # Utilities (340 lines)
│   ├── telecom_analyzer.py    # Verizon (370 lines)
│   └── amex_analyzer.py       # AMEX (341 lines)
│
├── shared/
│   ├── auth_manager.py        # OAuth 2.0 (260 lines)
│   ├── email_parser.py        # Email parsing (320 lines)
│   └── html_generator.py      # Jinja2 templates (400 lines)
│
├── templates/
│   ├── _base.html             # Base template
│   ├── utility_report.html    # Utility report
│   ├── telecom_report.html    # Telecom report
│   └── amex_report.html       # AMEX report
│
├── tests/
│   ├── unit/                  # 850+ lines of unit tests
│   └── integration/           # Orchestrator tests
│
├── ARCHITECTURE.md            # Complete system design
├── README.md                  # This file
├── requirements.txt           # Dependencies
└── docs/
    ├── BUSINESS_MODEL.md      # Business model
    ├── PRICING_STRATEGY.md    # Pricing strategy
    └── Additional guides...
```

## 🚀 Quick Start

### Installation

```bash
# Clone or navigate to the project
cd utility-analysis-tool

# Install dependencies
pip install -r requirements.txt
```

### Run Analyzers

```bash
# Run all 3 analyzers
python orchestrator.py

# Run specific analyzers only
python orchestrator.py --utility --telecom

# Generate HTML reports
python orchestrator.py --html

# Generate both JSON + HTML
python orchestrator.py --json --html

# List available analyzers
python orchestrator.py --list
```

### Output Files

Automatically generated in `reports/` and `data/` directories:

```
reports/
├── utility_report_TIMESTAMP.html       # Utility company analysis
├── telecom_report_TIMESTAMP.html       # Verizon bill analysis
├── amex_report_TIMESTAMP.html          # AMEX spending analysis
└── master_dashboard_TIMESTAMP.html     # Combined KPI dashboard

data/
├── utility_data_TIMESTAMP.json         # Utility JSON export
├── telecom_data_TIMESTAMP.json         # Telecom JSON export
├── amex_data_TIMESTAMP.json            # AMEX JSON export
└── aggregate_report_TIMESTAMP.json     # Combined JSON data
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/unit/test_gmail_utility_analyzer.py -v

# Run with coverage
pytest tests/ --cov=analyzers --cov=shared --cov-report=html
```

## 📊 Current Statistics

| Metric | Count |
|--------|-------|
| **Lines of Code** | 5,500+ |
| **Test Cases** | 298 |
| **Test Coverage** | 100% core |
| **Analyzers** | 3 |
| **Templates** | 4 |
| **Git Commits** | 7 |

## 🔐 Authentication

First run will prompt for Gmail OAuth login. Credentials are securely stored and auto-refreshed:

- `credentials.json` - OAuth client secrets (git-ignored)
- `token.json` - Access/refresh tokens (git-ignored, auto-managed)

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system design and data flows
- **[STRUCTURE.md](STRUCTURE.md)** - Directory organization
- **[WEEK1_COMPLETION.md](WEEK1_COMPLETION.md)** - Week 1 deliverables
- **claude.md** - Claude automation integration

## 🎯 Features

### ✅ Utility Analyzer
- Detects 8+ utility companies
- Extracts service types and regions
- Tracks email frequency

### ✅ Telecom Analyzer
- Verizon Fios & Wireless support
- Bill type detection
- Amount extraction

### ✅ AMEX Analyzer
- Card type detection (Platinum, Gold, Blue, etc.)
- Spending categorization (7 categories)
- Rewards point estimation

### ✅ Orchestrator
- Run individual or all analyzers
- Aggregate results
- Master HTML dashboard
- JSON data export

## 🛠️ Tech Stack

- **Language:** Python 3.9+
- **Gmail:** Google API Client (OAuth 2.0)
- **Templates:** Jinja2
- **Testing:** pytest + pytest-mock
- **Data:** JSON exports
- **HTML:** Custom Jinja2 templates with responsive design

## 🚢 Deployment Ready

- ✅ Production-grade code
- ✅ Full test coverage
- ✅ OAuth 2.0 authentication
- ✅ HTML + JSON output formats
- ✅ Error handling & logging
- ✅ Extensible architecture

Perfect for building customer-facing report generation services.
    └── OPERATIONS.md                  # How to deliver reports
```

## 💻 How to Generate a Report

### For You (Operator):
1. Receive customer utility PDFs (email/Typeform)
2. Extract bill data into the data template
3. Run the report generator
4. Customize with customer details
5. Send HTML + Excel files to customer
6. Done ✅

### For Customers:
1. Visit landing page (carrd.co link)
2. Click "Get Your Report"
3. Pay $79 via Stripe
4. Upload utility PDFs via Typeform
5. Receive comprehensive report in 24 hours

## 🛠️ Tech Stack

- **Frontend:** HTML5 + CSS3 + Chart.js (for interactive charts)
- **Payment:** Stripe (payment links)
- **Intake:** Typeform (PDF uploads)
- **Reporting:** Excel + HTML
- **Automation:** Zapier/Google Sheets integration (planned)
- **Hosting:** Carrd (landing page)

## 📈 Pricing Breakdown

| Service | Price | Time |
|---------|-------|------|
| Premium Analysis Report | $79 | 24-48 hours |
| Basic Report (future) | $39 | 48-72 hours |
| Annual Subscription (future) | $999/year | Unlimited reports |

## 🔄 Next Steps

1. **This Week:**
   - Launch Carrd landing page
   - Set up Stripe payment link
   - Create Typeform intake form

2. **Week 2:**
   - Automate intake workflow
   - Test full customer flow
   - Document procedures

3. **Week 3:**
   - Find first paying customer
   - Refine process based on feedback
   - Scale up marketing

## 📞 Customer Journey

```
Customer Sees Ad
        ↓
Lands on Carrd Page
        ↓
Clicks "Get Your Report"
        ↓
Completes $79 Payment (Stripe)
        ↓
Receives Typeform Link
        ↓
Uploads Utility PDFs
        ↓
You Get Notified
        ↓
Generate Report (Excel + HTML)
        ↓
Send to Customer Email
        ↓
Customer Reviews Analysis ✅
```

## 🤖 Claude Integration

This project uses Claude for:
- **Daily progress tracking** - Keeps you focused on 1 task per day
- **Report generation** - Helps structure and format analysis
- **Process documentation** - Creates SOPs for scaling

See [claude.md](claude.md) for details on the automation.

## 📝 License

This is a proprietary business project. All materials are confidential.

---

**Questions?** Check `claude.md` for how to use Claude for daily workflow.
