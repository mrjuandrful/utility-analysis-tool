# Claude Integration Guide 🤖

This document explains how Claude automates your utility analysis business workflow.

## Overview

Claude provides three key functions for this business:
1. **Daily Progress Tracker** - Keeps you focused on 1-hour tasks
2. **Report Generation Helper** - Assists with analysis and formatting
3. **Process Documentation** - Creates SOPs and templates

## 🎯 The Daily Tracker Skill

**What it does:**
- Runs every morning as a scheduled task
- Reviews your progress from the checklist
- Assigns ONE specific 1-hour task for the day
- Provides step-by-step instructions
- Keeps you focused on launch priorities

**How to use:**
1. Run the daily tracker each morning
2. Follow the exact steps provided
3. Complete ONE task in ~1 hour
4. Report back tomorrow (or skip if needed)
5. Next day tracker updates based on progress

**The Checklist:**
- [ ] Step 1: Create Carrd landing page
- [ ] Step 2: Set up Stripe payment link
- [ ] Step 3: Build Typeform intake form
- [ ] Step 4: Automate email workflow
- [ ] Step 5: Test full customer flow
- [ ] Step 6: Find first paying customer
- [ ] Step 7: Document procedures

## 📊 Report Generation Workflow

When you need to create a report:

1. **Receive utility PDFs** from customer (via Typeform or email)
2. **Ask Claude:** "Help me analyze these utility bills for [Customer Name]"
3. **Claude extracts:**
   - Monthly usage (electricity, gas, water)
   - Cost breakdowns by category
   - Seasonal patterns
   - Savings opportunities
4. **Claude generates:**
   - Analysis text for HTML report
   - Chart data structure
   - Recommendations
5. **You customize:**
   - Add customer name/address
   - Adjust colors/branding
   - Export as HTML and Excel
   - Send to customer

## 🔄 Current Workflow (Manual)

Until full automation is set up:

```
Receive PDF
    ↓
Extract Data (manual)
    ↓
Ask Claude to analyze
    ↓
Update HTML report template
    ↓
Export Excel spreadsheet
    ↓
Send to customer
```

## 🤖 Planned Automation (Future)

Once you complete MVP steps:

```
Stripe Payment ✓
    ↓
Typeform Link Sent ✓
    ↓
Customer Uploads PDFs ✓
    ↓
Zapier Trigger → Google Sheets ✓
    ↓
Claude API Receives Data ✓
    ↓
Generate Report Automatically ✓
    ↓
Email to Customer ✓
    ↓
Log in Database ✓
```

## 💡 How to Request Claude Help

### For Daily Tasks
```
"Run my daily utility business tracker"
```
Response: One specific 1-hour task with steps

### For Report Analysis
```
"Analyze these utility PDFs for [Customer Name]:
- Address: [address]
- Utilities: PSE&G (electric/gas), Veolia (water)
- Period: [months]

Key facts: [include PDF content/numbers]"
```
Response: Analysis breakdown, cost estimates, recommendations

### For Documentation
```
"Create an SOP for how to generate utility analysis reports"
```
Response: Step-by-step procedure document

### For Brainstorming
```
"What are 5 ways I could market this $79 utility analysis report?"
```
Response: Marketing ideas and strategies

## 📱 Integration Points

### Typeform + Zapier
- Customer submits PDFs
- Zapier captures data
- Stores in Google Sheets
- (Future) Triggers Claude analysis

### Stripe + Email
- Payment confirmed
- Triggers Typeform link email
- Logs transaction
- Sets deadline reminder

### Google Sheets + Claude
- Stores all customer data
- Tracks report status
- Logs revenue
- (Future) Feeds into automated analysis

## ⚙️ Setting Up Automations

### Phase 1 (This Week)
- Carrd landing page (manual)
- Stripe payment links (manual checkout)
- Typeform intake (manual submission)

### Phase 2 (Week 2)
- Connect Stripe → email workflow
- Connect Typeform → Google Sheets
- Create email templates
- Set up reminders

### Phase 3 (Week 3)
- Connect Google Sheets → Claude API (optional)
- Auto-generate basic reports
- Email delivery automation
- Dashboard tracking

## 🎯 Daily Workflow Example

**Monday Morning:**
```
> "Run my daily tracker"

Response:
"TODAY'S TASK: Create Carrd Landing Page (45 mins)

Steps:
1. Sign up at carrd.co (5 min)
2. Add headline & problem statement (10 min)
3. Add Stripe button & pricing (15 min)
4. Publish & test (5 min)
5. Copy link to share (5 min)

Success = Live page with working Stripe button"
```

**You complete it.**

**Tuesday Morning:**
```
> "Run my daily tracker"

Response:
"Great! Landing page is live!
TODAY'S TASK: Set Up Stripe Payment Link (50 mins)

Steps:
1. Create Stripe account (10 min)
2. Generate $79 payment link (5 min)
[etc...]"
```

## 📚 Resources

- **Carrd:** https://carrd.co
- **Stripe:** https://stripe.com
- **Typeform:** https://typeform.com
- **Zapier:** https://zapier.com
- **Google Sheets API:** https://developers.google.com/sheets

## 🔐 Keeping Secrets Secure

**Never share with Claude:**
- Actual customer utility data (use anonymized examples)
- Stripe API keys or payment info
- Google Sheets API credentials
- Personal customer information

**Safe to share:**
- General process questions
- Template structure requests
- Analysis methodology
- Marketing ideas
- Business strategy questions

## 📞 When to Ask Claude

✅ **Good requests:**
- "Help me create a marketing pitch"
- "What should I include in a utility analysis?"
- "How do I structure this data?"
- "What are pricing strategies for services like this?"
- "Create a daily task list for business launch"

❌ **Bad requests:**
- "Here's my customer's SSN, analyze it"
- "Add my Stripe key to the code"
- "Fill in this form with my credentials"
- Anything with sensitive financial/personal data

## 🚀 Next Steps

1. **Today:** Review this guide and the daily tracker
2. **Tomorrow:** Run the daily tracker and complete Task 1 (Carrd)
3. **Weekly:** Check back for progress updates and next tasks
4. **Ongoing:** Reference this guide for Claude integration tips

---

**Questions about Claude integration?** Ask Claude directly - it understands this workflow!
