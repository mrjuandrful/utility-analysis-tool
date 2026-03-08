# Zapier Automation Workflows - Complete Guide

## Overview
This guide sets up 3 automated workflows:
1. **Workflow 1:** Typeform Response → Store in Google Sheets (tracking)
2. **Workflow 2:** Typeform Response → Send confirmation email
3. **Workflow 3:** Typeform Response → Trigger your analysis process

---

## Prerequisites
Before starting, you need:
- [ ] Zapier account (free tier ok to start)
- [ ] Typeform live with your form
- [ ] Gmail account (already connected)
- [ ] Google Sheets account (for tracking)
- [ ] Google Drive folder for PDFs (optional but recommended)

---

## WORKFLOW 1: New Response → Google Sheets (Tracking Dashboard)

### What this does:
Every time someone fills out your form, a new row is added to a Google Sheet with their info. This becomes your customer list and tracking dashboard.

### Step-by-step:

1. **Go to Zapier.com** and sign in
2. **Create New Zap**
3. **Set Trigger:**
   - App: Typeform
   - Event: "New Response"
   - Account: Connect your Typeform account
   - Form: "Utility Bill Analysis - Beta Testing"
   - Click "Continue"

4. **Test Trigger:**
   - Zapier will fetch a sample response
   - Click "Continue" once test passes

5. **Add Action:**
   - Click "Add a Step"
   - App: Google Sheets
   - Event: "Create Spreadsheet Row"
   - Account: Connect your Google account
   - Spreadsheet: Create new or select existing
   - Worksheet: "Beta Responses" (or any name)

6. **Map Fields to Columns:**
   ```
   Column A: Response ID (Typeform Response ID)
   Column B: Timestamp (Submitted At)
   Column C: Name (Name field)
   Column D: Email (Email field)
   Column E: Address (Address field)
   Column F: Utilities (Utility Types)
   Column G: Companies (Utility Companies)
   Column H: Main Goal (What interested them most)
   Column I: Status (Start with "Received")
   Column J: Date Started (Leave blank - you'll update manually)
   Column K: Analysis Link (Leave blank - you'll add later)
   ```

7. **Test Action:**
   - Click "Test & Continue"
   - Check Google Sheets to verify row was added

8. **Turn on Zap:**
   - Name it: "Typeform to Google Sheets - Beta Tracking"
   - Click "Publish"

---

## WORKFLOW 2: New Response → Send Welcome Email

### What this does:
Automatically sends a professional welcome email to the customer immediately after they submit the form.

### Step-by-step:

1. **Create New Zap** (same Typeform trigger as Workflow 1)
2. **Trigger Setup:** (Same as Workflow 1, steps 3-4)

3. **Add Action:**
   - App: Gmail
   - Event: "Send Email"
   - Account: Connect your Gmail
   - To: Use Typeform Email field
   - From: mrjuandrful@gmail.com
   - Subject:
     ```
     ✅ Your Utility Bill Analysis is On the Way!
     ```

4. **Email Body:**
   ```
   Hi {{1. Name}},

   Thank you for submitting your utility bills! 🎉

   Here's what happens next:
   ✓ I'm analyzing your bills right now
   ✓ You'll get your personalized report within 24 hours
   ✓ The report includes charts, trends, and savings recommendations

   📊 What to expect in your report:
   • Monthly cost breakdown by utility
   • Appliance-by-appliance energy estimates
   • Seasonal spending patterns
   • Actionable recommendations to save money
   • Professional HTML report + Excel spreadsheet

   Need anything in the meantime? Reply to this email - I check constantly.

   Looking forward to helping you understand your bills better!

   Best,
   Juan Perez
   Utility Analysis
   mrjuandrful@gmail.com

   P.S. In the meantime, check out our EV vs Gas Savings Calculator:
   [your-domain.com/ev-calculator]
   ```

5. **Test & Publish:**
   - Name: "Typeform to Gmail - Welcome Email"
   - Test it, then publish

---

## WORKFLOW 3: New Response → Create Task/Notification

### What this does:
Sends YOU a notification so you know someone submitted. Helps you prioritize analysis work.

### Step-by-step:

1. **Create New Zap** (same Typeform trigger)

2. **Add Action:**
   - App: Gmail (or Slack if you use it)
   - Event: "Send Email"
   - To: mrjuandrful@gmail.com
   - Subject:
     ```
     🎯 New Beta Signup: {{1. Name}}
     ```

3. **Email Body:**
   ```
   Name: {{1. Name}}
   Email: {{2. Email}}
   Address: {{3. Address}}
   Utilities: {{4. Utilities}}
   Companies: {{5. Companies}}
   Main Goal: {{6. Main Goal}}
   Special Questions: {{7. Special Questions}}

   PDFs Uploaded: Yes
   Status: Ready for Analysis
   Timestamp: {{Submitted At}}

   ⚡ ACTION ITEM:
   1. Download PDFs from Typeform
   2. Run Gmail Analyzer and create report
   3. Send report back to {{2. Email}}
   4. Update Google Sheet with analysis link
   ```

4. **Test & Publish:**
   - Name: "Typeform - Notify Me of New Responses"
   - Publish

---

## WORKFLOW 4 (Optional): Auto-Download PDFs to Google Drive

### What this does:
Automatically saves all uploaded PDFs to a Google Drive folder for backup and easy access.

### Step-by-step:

1. **Create New Zap** (same Typeform trigger)

2. **Add Action:**
   - App: Google Drive
   - Event: "Upload File"
   - Account: Connect Google Drive
   - Drive: "My Drive"
   - Folder: Create folder "Utility Bills - Beta"

3. **Map:**
   - File Name: `{{1. Name}} - {{Submitted At Date}}`
   - File Content: Typeform File (Bill PDF)

4. **Test & Publish:**
   - Name: "Typeform PDFs to Google Drive"

---

## Testing All Workflows

### Test Submission:
1. Fill out your Typeform yourself
2. Check that all 3 workflows trigger:
   - ✓ Row appears in Google Sheets
   - ✓ Welcome email arrives
   - ✓ You get notified
   - ✓ PDFs backed up to Drive (if Workflow 4)

### Expected Results:
```
Timeline:
T+0 sec: Form submitted
T+5 sec: Google Sheets updated
T+10 sec: Welcome email sent
T+10 sec: Your notification sent
T+30 sec: PDFs backed up to Drive
```

---

## Your Checklist

- [ ] Zapier account created
- [ ] All 3 workflows set up
- [ ] Test submission completed
- [ ] All zaps are "on"
- [ ] Google Sheet created and accessible
- [ ] Emails being sent correctly
- [ ] You're receiving notifications

---

## Next Steps (After Zapier is Working)

1. **Create the analysis workflow:**
   - When you get notified, download PDFs
   - Run your analysis tools (Gmail Analyzer, manual review)
   - Generate HTML report
   - Email report to customer

2. **Automate report generation (Future):**
   - Set up Python script to auto-generate reports
   - Integrate with your analysis tools
   - Email reports directly from automation

3. **Track completion:**
   - Update Google Sheet status when analysis is done
   - Add analysis link to Google Sheet
   - Customer can see their link in follow-up email

---

## Troubleshooting

**Zap isn't triggering?**
- Check that Typeform account is connected
- Make sure form is selected (not drafts)
- Test the trigger again

**Emails not arriving?**
- Check Gmail spam folder
- Verify email template syntax (use {{ }})
- Test with your own email first

**Google Sheets not updating?**
- Verify spreadsheet and sheet name are correct
- Check column mapping matches your columns
- Make sure sheet isn't read-only

**File upload failing?**
- Ensure Google Drive folder exists
- Check that Drive account is properly connected
- Try uploading smaller test file

---

## Cost Notes

**Free Tier Limits:**
- Zapier free = 100 tasks/month
- You have 3 workflows = ~30 responses before hitting limit
- Perfect for beta testing!

**Upgrade when you need:**
- $20/month for 1000 tasks (plenty for small business)
- Pay-as-you-go after free tier

---

## Zap Status Dashboard

After setting up, your Zapier dashboard will show:

```
✅ Workflow 1: Typeform → Google Sheets (ON)
✅ Workflow 2: Typeform → Welcome Email (ON)
✅ Workflow 3: Typeform → Notify You (ON)
✅ Workflow 4: Typeform → Google Drive (ON)

Total Tasks Run This Month: [X]
Tasks Remaining: [100 - X]
```

Monitor this to know when to upgrade.

---

## Email Template Variables Reference

When writing emails in Zapier, use these variables from Typeform:

```
{{1. Name}} = Customer's full name
{{2. Email}} = Customer's email
{{3. Address}} = Customer's address
{{4. Utilities}} = Selected utility types
{{5. Companies}} = Utility companies listed
{{6. Main Goal}} = What they wanted to learn
{{7. Special Questions}} = Their specific questions
{{Submitted At}} = Full timestamp
{{Submitted At Date}} = Just the date
{{Response ID}} = Unique response ID
```

Example email subject:
```
Hi {{1. Name}}, your analysis for {{3. Address}} is ready!
```

---

## Done! ✅

Your automation is now live:
- Customers submit form
- They get instant welcome email
- You get notified
- Data tracked in Google Sheets
- PDFs backed up
- You can now focus on analysis!
