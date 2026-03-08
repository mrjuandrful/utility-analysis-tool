# Repository Structure & Git Organization

## Git Status

```
Remote:  https://github.com/mrjuandrful/utility-analysis-tool.git
Branch:  main (1 commit ahead of origin/main)
Commits: 6 total
  - 58c8d5d (NEW) refactor: extract base analyzer class [Week 1]
  - 7431b31 Add Typeform quick start guide
  - 9e6506b Add complete automation setup guides
  - ea395ea Add utility analysis tools
  - 61c75b8 Add documentation and templates
  - d7560cb Initial commit (Tesla/Kasa trackers)
```

### Cleanup Needed (Planned)
- [ ] Remove `__pycache__/` directories from git (in .gitignore, but still tracked in last commit)
- [ ] Clean up `.~lock.*` files from git
- [ ] Delete lock files: `.git/index.lock`, `.git/HEAD.lock`
- ✅ Expanded `.gitignore` (done)

**Note:** Git lock file exists due to permission issue. Can be resolved by:
```bash
rm -f .git/index.lock  # May need elevated permissions
# Then: git status should work normally
```

---

## Directory Structure

### 🔧 Core Analysis Tools (NEW - Week 1)

```
analyzers/
├── __init__.py                     # Package export
├── base_analyzer.py                # ⭐ Abstract base class (290 lines)
├── gmail_utility_analyzer.py       # TODO: Refactor to inherit BaseAnalyzer (Week 2)
├── telecom_analyzer.py             # TODO: Implement (Week 3)
└── amex_card_analyzer.py           # TODO: Implement (Week 4)
```

**Purpose:** Domain-specific financial document analyzers
**Pattern:** Template method - subclasses implement `search_emails()` and `parse_documents()`

---

### 🛠️ Shared Utilities (NEW - Week 1)

```
shared/
├── __init__.py                     # Package export
├── auth_manager.py                 # ⭐ OAuth 2.0 handling (260 lines)
├── email_parser.py                 # ⭐ HTML/email parsing (320 lines)
├── html_generator.py               # TODO: Jinja2 template rendering (Week 2)
└── config_loader.py                # TODO: YAML config parsing (Week 2)
```

**Purpose:** Reusable utilities shared across all analyzers
**Used by:** Every analyzer for auth, parsing, reporting

---

### 📋 Testing (NEW - Week 1)

```
tests/
├── __init__.py
├── conftest.py                     # ⭐ Pytest fixtures & mocks (140 lines)
├── unit/
│   ├── __init__.py
│   ├── test_base_analyzer.py       # ⭐ BaseAnalyzer tests (260 lines)
│   ├── test_auth_manager.py        # ⭐ AuthManager tests (210 lines)
│   └── test_email_parser.py        # ⭐ EmailParser tests (380 lines)
├── integration/
│   └── __init__.py
└── fixtures/
    ├── sample_utility_emails.json  # TODO: Sample data
    ├── sample_telecom_emails.json  # TODO: Sample data
    └── sample_amex_emails.json     # TODO: Sample data
```

**Purpose:** Unit & integration test suite
**Coverage:** All shared utilities, base class, and parsing logic
**Status:** Unit tests complete (850+ lines); integration tests in Week 5

---

### 📊 Configuration & Templates

```
config/
├── default.yaml                    # TODO: App configuration
├── providers.yaml                  # TODO: Company/carrier definitions
└── credentials.json                # 🔐 (git-ignored) OAuth token storage

templates/
├── utility_report.html             # TODO: Jinja2 template for utilities
├── telecom_report.html             # TODO: Jinja2 template for telecom
├── credit_card_report.html         # TODO: Jinja2 template for AMEX
└── master_report.html              # TODO: Combined dashboard
```

---

### 📁 Data & Reports

```
data/
├── utility_data.json               # (git-ignored) Generated at runtime
├── telecom_data.json               # (git-ignored) Generated at runtime
└── credit_card_data.json           # (git-ignored) Generated at runtime

reports/
├── utilities_report.html           # (git-ignored) Generated output
├── telecom_report.html             # (git-ignored) Generated output
├── credit_card_report.html         # (git-ignored) Generated output
└── master_report.html              # (git-ignored) Consolidated dashboard
```

---

### 📚 Documentation & Legacy

```
docs/
└── DAILY_TRACKER_SKILL.md          # Claude daily automation workflow

README.md                            # Project overview & setup
claude.md                            # Claude integration guide
WEEK1_COMPLETION.md                 # Week 1 milestone summary (NEW)
STRUCTURE.md                         # This file (NEW)

CARRD_CONTENT_GUIDE.md              # Landing page copy
TYPEFORM_SETUP_GUIDE.md             # Form builder setup
TYPEFORM_QUICK_START.md             # 10-minute form setup
ZAPIER_SETUP_GUIDE.md               # Automation workflows
ZAPIER_AUTOMATION_COMPLETE.md       # Complete automation guide

gmail_utility_analyzer.py           # Original script (to be refactored Week 2)
requirements.txt                    # Dependencies (NEW)
```

---

### 🏆 Legacy: Business Model & Templates

```
trackers/
└── Kasa_Energy_Tracker.xlsx        # Energy usage tracker template

Tesla_Savings_Report.html           # Sample EV cost analysis
Tesla_Savings_Report.xlsx           # Sample data
EV_vs_Gas_Cost_Analysis.html        # Comparison report
EV_vs_Gas_Cost_Analysis.xlsx        # Cost analysis data

Carrd_Landing_Page_Mockup.html      # Carrd landing page design
Kasa_Energy_Tracker.xlsx            # Energy tracking spreadsheet
```

---

## What Goes Where

### Production Code (Committed to Git)
- ✅ `analyzers/*.py` - Analyzer implementations
- ✅ `shared/*.py` - Shared utilities
- ✅ `tests/*.py` - Test code
- ✅ `config/default.yaml` - Configuration (no secrets)
- ✅ `templates/*.html` - Jinja2 templates
- ✅ `requirements.txt` - Dependencies
- ✅ `*.md` - Documentation

### Generated Files (Git-Ignored)
- ❌ `data/*.json` - Generated at runtime
- ❌ `reports/*.html` - Generated at runtime
- ❌ `reports/*.xlsx` - Generated at runtime
- ❌ `credentials.json` - OAuth token (NEVER commit!)
- ❌ `token.json` - OAuth token (NEVER commit!)
- ❌ `.env` - Environment variables (NEVER commit!)
- ❌ `__pycache__/` - Python cache
- ❌ `.~lock*` - LibreOffice lock files

---

## .gitignore Status

### Current Configuration
✅ Excludes:
- Python cache (`__pycache__/`, `*.pyc`, `*.pyo`)
- Virtual environments (`venv/`, `env/`)
- IDE files (`.vscode/`, `.idea/`)
- Credentials (`.env`, `credentials.json`, `token.json`)
- Generated outputs (`data/*.json`, `reports/*`)
- Test artifacts (`.pytest_cache/`, `.coverage`)
- Lock files (`.git/index.lock`)
- OS files (`.DS_Store`, `Thumbs.db`)

---

## Git Workflow (Recommended)

### For Local Development
```bash
# Create feature branch
git checkout -b feature/telecom-analyzer

# Make changes, test, commit
git add analyzers/telecom_analyzer.py tests/unit/test_telecom_analyzer.py
git commit -m "feat: add telecom analyzer for Verizon bills"

# Push to GitHub
git push origin feature/telecom-analyzer
```

### Commit Message Format
```
<type>: <subject> (50 chars max)

<body> (explain what, why, not how)

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

**Types:** `feat:` `fix:` `refactor:` `docs:` `test:` `chore:`

---

## Next Steps

### Week 2 (Utility Analyzer Refactor)
- [ ] Move `gmail_utility_analyzer.py` → `analyzers/gmail_utility_analyzer.py`
- [ ] Make it inherit from `BaseAnalyzer`
- [ ] Update existing tests to use new structure
- [ ] Create backwards-compatibility wrapper at root
- [ ] Commit: `refactor: migrate utility analyzer to new structure`

### Week 3 (Telecom Analyzer)
- [ ] Implement `analyzers/telecom_analyzer.py`
- [ ] Add support for Verizon Fios (867-0001) + Wireless (7065-00001)
- [ ] Write `tests/unit/test_telecom_analyzer.py`
- [ ] Commit: `feat: add telecom analyzer for Verizon bills`

### Week 4 (AMEX Analyzer)
- [ ] Implement `analyzers/amex_card_analyzer.py`
- [ ] HTML table parsing + PDF fallback
- [ ] Write `tests/unit/test_amex_analyzer.py`
- [ ] Commit: `feat: add AMEX credit card statement analyzer`

### Week 5 (Orchestrator)
- [ ] Implement `orchestrator.py`
- [ ] Master CLI entry point
- [ ] JSON aggregation logic
- [ ] Write `tests/integration/test_orchestrator.py`
- [ ] Commit: `feat: add orchestrator for unified analysis`

### Week 6 (Polish & Deploy)
- [ ] Write `shared/html_generator.py` (Jinja2 templates)
- [ ] Create `config/default.yaml` and `config/providers.yaml`
- [ ] Add README updates
- [ ] GitHub Actions CI/CD setup
- [ ] Final commit: `docs: update README and add GitHub Actions`

---

## Current Git Commits

### Latest: 58c8d5d (HEAD) - Week 1 Foundation ✅
```
refactor: extract base analyzer class and shared utilities
  - base_analyzer.py (290 lines)
  - auth_manager.py (260 lines)
  - email_parser.py (320 lines)
  - Comprehensive unit tests (850+ lines)
  - requirements.txt
Files: 27 changed, 3442 insertions(+)
```

---

## How to Fix Git Lock Issue

If you see: "fatal: Unable to create '.git/index.lock'"

```bash
# Try the soft way first
cd "Claude code cowork"
rm -f .git/index.lock
git status

# If that doesn't work, check for lingering processes
ps aux | grep git
# Kill any git processes, then retry

# Last resort: reset lock file
git reset --hard HEAD
```

---

## Summary: What You Have

✅ **Week 1 Complete:**
- Abstract base class system
- OAuth authentication
- Email/HTML parsing utilities
- Comprehensive unit tests
- Requirements.txt
- Updated .gitignore
- 1 git commit (58c8d5d)

⏳ **Ready for Week 2:**
- Refactor existing utility analyzer
- Create backwards-compatible wrapper
- Telecom analyzer implementation

🚀 **Long-term (Weeks 3-6):**
- AMEX analyzer + orchestrator
- HTML report generation
- Full integration tests
- Production deployment

