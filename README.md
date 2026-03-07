# Utility Analysis Tool 💡

A done-for-you utility bill analysis service that helps homeowners understand their energy spending and savings opportunities.

## 🎯 Business Model

**Service:** Professional utility bill analysis reports
**Price:** $79 per comprehensive report
**Delivery:** HTML report + Excel spreadsheets
**Time to deliver:** 24-48 hours

## 📊 What's Included

Each analysis report covers:
- ✅ **Complete utility breakdown** - Electricity, gas, water costs by month
- ✅ **Cost-by-appliance estimates** - Where your money actually goes
- ✅ **Seasonal trend analysis** - Why bills vary throughout the year
- ✅ **Savings opportunities** - Actionable recommendations
- ✅ **EV charging analysis** - (If applicable) Fuel cost comparisons
- ✅ **Visual charts** - Easy-to-understand trends and patterns

## 🚀 Current Status

**Completed:**
- ✅ Report template (HTML with styling & interactivity)
- ✅ Business model validated
- ✅ Pricing strategy set
- ✅ Sample reports delivered

**In Progress (MVP Launch):**
- Landing page (Carrd)
- Payment processing (Stripe)
- Customer intake form (Typeform)
- Automation workflow
- Beta customer testing

## 📁 Project Structure

```
utility-analysis-tool/
├── README.md                          # You are here
├── claude.md                          # Claude automation guide
├── reports/
│   ├── Tesla_Savings_Report.html      # Sample report template
│   └── Tesla_Savings_Report.xlsx      # Sample data spreadsheet
├── trackers/
│   └── Kasa_Energy_Tracker.xlsx       # Energy usage tracking template
└── docs/
    ├── BUSINESS_MODEL.md              # Detailed business model
    ├── PRICING_STRATEGY.md            # Pricing and packaging
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
