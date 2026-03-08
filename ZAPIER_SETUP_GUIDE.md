# 🤖 Utility Analysis Automation - Zapier Setup Guide

## Overview

This guide walks you through setting up **fully automated utility bill analysis** using Zapier + Claude API. When a customer submits their utility PDFs through forms.app, Claude will automatically analyze them and email back a formatted HTML report.

---

## Prerequisites

Before starting, make sure you have:

✅ **Claude API Key** (from console.anthropic.com)
✅ **Zapier Free Account** (zapier.com/sign-up)
✅ **Gmail Account** (for sending emails)
✅ **forms.app Form** (https://6aurd234.forms.app/utility-bill-analysis-signup-form)

---

## Step 1: Get Your API Keys

### 1.1 Claude API Key

1. Go to **console.anthropic.com**
2. Log in or create account
3. Click **"Create New API Key"**
4. Copy and save the key securely
5. Add **$10-20 in credits** to your account

### 1.2 Zapier Account

1. Go to **zapier.com/sign-up**
2. Sign up with your email
3. Free tier gives you **100 tasks/month** (plenty for beta testers!)

---

## Step 2: Create Your Zapier Workflow

### 2.1 Create New Zap

1. Log into **Zapier**
2. Click **"Create"** → **"New Zap"**
3. Name it: `Utility Analysis Auto-Report`

### 2.2 Step 1: Set Trigger (forms.app Submission)

1. Click **"Add Trigger"**
2. Search for **"forms.app"** and select it
3. Select **"New Submission"**
4. **Connect your forms.app account** (allow permissions)
5. Select form: **"Utility Bill Analysis Signup Form"**
6. Click **"Test"** and submit a test entry to forms.app to verify connection

---

## Step 3: Add Claude API Action

### 3.1 Configure Claude API Call (Using Webhooks)

1. Click **"Add Action"** (after trigger)
2. Search for **"Webhooks by Zapier"**
3. Select **"POST"**

**Fill in these fields:**

| Field | Value |
|-------|-------|
| **URL** | `https://api.anthropic.com/v1/messages` |
| **Method** | `POST` |
| **Headers** | `x-api-key: [YOUR_CLAUDE_API_KEY]`<br/>`content-type: application/json` |

### 3.2 Request Body (JSON)

Copy and paste this exact JSON into the **"Data"** field:

```json
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4096,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Analyze these utility bills for {{fullName}} at {{address}}. Provide ONLY a JSON response (no markdown) with exactly these fields: {cost_electricity_total, kwh_total, cost_gas_total, therms_total, cost_water_total, total_6months, monthly_breakdown: [{month: 'Aug', electric: X, gas: X, water: X}...], key_insights: ['insight 1', 'insight 2'...], recommendations: ['rec 1', 'rec 2'...]}"
        },
        {
          "type": "document",
          "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": "{{pdfBase64}}"
          }
        }
      ]
    }
  ]
}
```

**IMPORTANT:** Map these Zapier variables from forms.app:
- `{{fullName}}` → Full Name field from form
- `{{address}}` → Address field from form
- `{{pdfBase64}}` → Base64-encoded PDF from file upload (Zapier will handle encoding)

---

## Step 4: Add Gmail Action

### 4.1 Configure Email

1. Click **"Add Action"**
2. Search **"Gmail"**
3. Select **"Send Email"**
4. Connect your Gmail account

### 4.2 Email Settings

| Field | Value |
|-------|-------|
| **To** | `{{emailAddress}}` (from forms.app submission) |
| **Subject** | `📊 Your Utility Analysis Report - {{fullName}}` |
| **Body** | Use HTML template below (see Step 5) |
| **Is HTML** | ✅ YES |

---

## Step 5: Use HTML Email Template

Create an HTML email template with the Claude API response data. The template is in your repository:

**File:** `/reports/Utility_Analysis_Template.html`

**How to use:**
1. Copy the template
2. Replace placeholder variables with Zapier data:
   - `[CUSTOMER_NAME]` → `{{fullName}}`
   - `[ADDRESS]` → `{{address}}`
   - `[COST_ELECTRICITY]` → Claude API response
   - `[COST_GAS]` → Claude API response
   - etc.

---

## Step 6: Test Your Zap

### Before Going Live:

1. **Test with your own PDFs**
   - Go to forms.app
   - Fill out the form with test data
   - Upload your own utility bill PDFs

2. **Check your email**
   - Did you receive the report?
   - Is the data correct?
   - Are the calculations accurate?
   - Is the HTML formatting good?

3. **Fix any issues**
   - If Claude API returns errors, check:
     - API key is correct
     - PDF is readable (not scanned/image-only)
     - All form fields are filled
   - If email didn't send, check:
     - Email address is valid
     - Gmail account is connected
     - HTML template is valid

4. **Turn on the Zap**
   - Once everything works, click the **toggle to ON**
   - Your automation is now live!

---

## Step 7: Monitor and Optimize

### First Week:
- ✅ Watch for test submissions
- ✅ Check emails are being sent
- ✅ Monitor API usage (console.anthropic.com)
- ✅ Get feedback from testers

### Optimization:
- Adjust prompt if Claude misses data
- Improve HTML template based on feedback
- Add more fields to the analysis as needed

---

## Troubleshooting

### Claude API returns errors
- **"Invalid API key"** → Check your key is copied correctly (no extra spaces)
- **"Could not process PDF"** → PDF might be scanned/image-only. Try text-based PDF
- **"Rate limit exceeded"** → You've hit API rate limits. Add more credits

### Email not sending
- **"Invalid email"** → Check forms.app has correct email field mapping
- **"Gmail authentication failed"** → Reconnect Gmail in Zapier
- **"HTML formatting error"** → Validate HTML template syntax

### Form not triggering
- **"No new submissions detected"** → Check forms.app is connected correctly
- **"Webhook failed"** → Verify Claude API URL is exactly: `https://api.anthropic.com/v1/messages`

---

## Cost Estimate

| Item | Cost |
|------|------|
| Claude API per PDF analysis | ~$0.15 |
| Zapier (free tier) | FREE |
| Gmail | FREE |
| **Total per customer** | **~$0.15** |

**Example:** 100 beta testers = ~$15 in API costs

---

## Next Steps

1. ✅ Get your API keys
2. ✅ Create Zapier account
3. ✅ Follow steps above to build the zap
4. ✅ Test with your own PDFs
5. ✅ Share form link with beta testers
6. ✅ Monitor submissions and get feedback

---

## Support

If you hit issues:
1. Check this guide's Troubleshooting section
2. Check Zapier docs: https://zapier.com/help/
3. Check Claude API docs: https://docs.anthropic.com/
4. Test each step independently (trigger → API → email)

Good luck with your beta launch! 🚀
