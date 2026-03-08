# Typeform Setup Guide - Utility Bill Analysis Form

## Overview
This Typeform collects customer information and utility bill PDFs, then integrates with Zapier to automate the workflow.

---

## Step-by-Step Setup

### 1. Create New Typeform
- Go to [typeform.com](https://typeform.com)
- Click "Create a new form"
- Choose "Blank form"
- Name: "Utility Bill Analysis - Beta Testing"

---

## Form Questions (in exact order)

### Question 1: Welcome Screen
**Type:** Welcome/Cover
```
Title: Welcome to Utility Analysis!
Description: We'll analyze your utility bills to show you exactly where your money goes.

Button Text: Start
```

---

### Question 2: Full Name
**Type:** Short Text
```
Question: What's your full name?
Placeholder: John Doe
```

---

### Question 3: Email Address
**Type:** Email
```
Question: What's your email address?
Description: We'll send your analysis here
Placeholder: you@example.com
```

---

### Question 4: Street Address
**Type:** Short Text
```
Question: What's your street address?
Description: (For location context - helps us understand regional utility rates)
Placeholder: 123 Main St, Maywood, NJ 07607
```

---

### Question 5: Utility Types
**Type:** Multiple Choice
```
Question: Which utilities do you have?
Description: Select all that apply
Options:
  - Electricity only
  - Natural Gas only
  - Electricity + Gas
  - Electricity + Gas + Water
  - Other (water only, solar, etc.)
```

---

### Question 6: Utility Companies
**Type:** Long Text
```
Question: Which utility companies serve you?
Description: List the names and service types
Placeholder: Example: PSEG (electric/gas), Veolia (water), Verizon (internet)
```

---

### Question 7: Upload Utility Bills
**Type:** File Upload
```
Question: Please upload your utility bill PDFs
Description: We need 3-6 months of recent bills. You can upload multiple files.
Allowed File Types: PDF only
Multiple Files: Yes
```

---

### Question 8: What's Your Main Goal?
**Type:** Multiple Choice
```
Question: What are you most interested in understanding?
Description: Select your top 3 priorities
Options:
  - Why my bill is so high
  - Monthly cost breakdown
  - Which appliances use most energy
  - Seasonal trends (winter vs summer)
  - Savings recommendations
  - Payment options/billing credits
  - Comparison to average customers
  - Solar/renewable energy options
```

---

### Question 9: Specific Questions
**Type:** Long Text
```
Question: Do you have any specific questions about your bills?
Description: (Optional) Help us tailor your analysis
Placeholder: Examples: Why does my bill spike in winter? Am I on the best rate plan?
```

---

### Question 10: Confirmation Screen
**Type:** Thank You / Confirmation
```
Title: ✅ Thank You!
Description: Your utility bills have been received.

We'll analyze them and send your personalized report within 24 hours.

In the meantime, check out our free EV vs Gas savings calculator.

Button Text: View Calculator
Button Link: [Your website or calculator link]
```

---

## Typeform Settings

### General
- **Form Name:** Utility Bill Analysis - Beta Testing
- **Make it private:** Yes (only accessible via direct link)

### Notifications
- **Email on new response:** mrjuandrful@gmail.com
- **Show progress bar:** Yes (helps with form completion)

### Design
- Choose a clean, professional template
- Use your brand colors (recommend: dark theme with cyan accent)
- Font: Any modern sans-serif is fine

### Share Settings
- Get your form URL (format: `https://mrjuandrful.typeform.com/to/XXXXXX`)
- Copy this URL for your Carrd button

---

## Integration with Zapier (Task E)

Once form is live, you'll use this Typeform trigger in Zapier:

**Trigger:** "New Typeform Response"
- Select form: "Utility Bill Analysis - Beta Testing"

**Data available in Zapier:**
- Name
- Email
- Address
- Utility Types
- Utility Companies
- Bill PDFs (files)
- Main Goal (array of selections)
- Specific Questions
- Response ID
- Timestamp

---

## Testing the Form

Before going live:

1. **Test the form yourself:**
   - Fill it out with your own info
   - Upload actual sample PDFs
   - Verify all fields work

2. **Check confirmation:**
   - Did you get the thank you screen?
   - Did you receive the email notification?

3. **Verify file upload:**
   - Can you upload PDFs?
   - Are files actually being captured?

4. **Test Zapier integration:**
   - Submit a test response
   - Check if Zapier picks it up
   - Verify all fields are pulling through

---

## Sharing Your Form

Once tested and verified:

1. **Get the form URL** from Typeform share page
2. **Update Carrd button link** with this URL
3. **Share with beta testers:**
   - Email the Typeform link directly
   - Share via social media
   - Include in your email signature

---

## Checklist

- [ ] Typeform created
- [ ] All 10 questions added
- [ ] File upload configured for PDFs
- [ ] Thank you screen customized
- [ ] Email notifications enabled
- [ ] Form tested with sample data
- [ ] Form URL copied
- [ ] Carrd button updated with form URL
- [ ] Ready for Zapier integration

---

## Form URL (Update after creating)

```
https://mrjuandrful.typeform.com/to/XXXXXX
```

Once you have your live URL, update:
- Carrd button link
- Email to beta testers
- All marketing materials
