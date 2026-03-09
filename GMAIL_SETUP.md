# Gmail OAuth 2.0 Setup Guide

## ✅ Status Check
- ✓ All analyzers created and tested
- ✓ HTML templates validated with mock data
- ✓ Orchestrator ready to scan Gmail
- ⏳ Awaiting: Gmail OAuth 2.0 credentials

## 🔐 Google Cloud Setup (One-time)

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Enter project name: **"Financial Document Analyzer"**
4. Click "Create"
5. Wait for project to be created (1-2 minutes)

### Step 2: Enable Gmail API
1. In the Cloud Console, search for **"Gmail API"**
2. Click on "Gmail API" from results
3. Click the **"ENABLE"** button
4. Wait for it to be enabled

### Step 3: Create OAuth 2.0 Credentials
1. Go to **"Credentials"** in the left sidebar
2. Click **"+ Create Credentials"** button
3. Choose **"OAuth 2.0 Client ID"** (if prompted, first create OAuth consent screen)

**If asked to configure consent screen first:**
1. Click "Create Consent Screen"
2. Choose **User Type: External**
3. Fill in:
   - App name: Financial Document Analyzer
   - User support email: mrjuandrful@gmail.com
   - Developer contact: mrjuandrful@gmail.com
4. Click "Save and Continue"
5. Skip optional scopes, click "Save and Continue"
6. Click "Back to Dashboard"

**Back to create credentials:**
1. Click "**+ Create Credentials**" → "**OAuth 2.0 Client ID**"
2. Choose **Application Type: Desktop application**
3. Name: **Financial Analyzer Desktop**
4. Click "**Create**"

### Step 4: Download Credentials
1. Look for the new credential in the Credentials list
2. Click the **download icon** (⬇️) on the right
3. A file named `client_secret_*.json` will download
4. **Rename it to `credentials.json`**

### Step 5: Add Credentials to Project
1. In your file explorer, navigate to:
   ```
   Documents/Claude code cowork/config/
   ```
2. Place `credentials.json` file in the `config/` folder
3. The path should be: `config/credentials.json`

## 🚀 Running the Scanner

### First Run (Will open browser for authentication)
```bash
cd "Documents/Claude code cowork"
python orchestrator.py --utility --telecom --amex --html
```

**What happens:**
1. A browser window opens asking to "Sign in with Google"
2. Sign in with your Gmail account (mrjuandrful@gmail.com)
3. Google asks for permission to access Gmail
4. Click "Allow"
5. You'll be redirected to a success page
6. The script creates `token.pickle` (saves authentication)
7. Scanning begins automatically

### Subsequent Runs (Uses saved token)
```bash
python orchestrator.py --utility --telecom --amex --html
```

No browser needed - the script uses the saved token from first run.

## 📄 Output Files

After scanning completes, check the `reports/` folder:

```
reports/
├── aggregate_results.json      (All data in JSON format)
├── dashboard.html              (Master overview of all findings)
├── utility_report.html         (Utility companies identified)
├── telecom_report.html         (Telecom services identified)
└── amex_report.html            (Credit card spending analysis)
```

## 🔧 CLI Options

```bash
# Run all analyzers
python orchestrator.py --utility --telecom --amex --html

# Run specific analyzer
python orchestrator.py --utility --html
python orchestrator.py --telecom --html
python orchestrator.py --amex --html

# Export to JSON instead of HTML
python orchestrator.py --utility --telecom --amex --json

# Both HTML and JSON
python orchestrator.py --utility --telecom --amex --html --json

# List available analyzers
python orchestrator.py --list
```

## 🔒 Security Notes

- **`credentials.json`**: Do NOT commit to git (in .gitignore)
- **`token.pickle`**: Auto-generated after first auth, safe to ignore
- **No data stored**: All processing happens locally
- **Gmail access scope**: Read-only, can only read emails
- **Revoke access anytime**:
  1. Go to [Google Account Security](https://myaccount.google.com/security)
  2. Find "Financial Document Analyzer"
  3. Click "Remove access"

## 🆘 Troubleshooting

### "credentials.json not found"
- Make sure you placed `credentials.json` in `config/` folder
- Path should be: `Documents/Claude code cowork/config/credentials.json`

### "Google couldn't verify this is a safe app"
- This is normal for new OAuth apps
- Click **"Advanced"** → **"Go to Financial Document Analyzer (unsafe)"**
- This is safe - it's your own app

### Token expired
- Delete `token.pickle` file
- Run scanner again - it will re-authenticate

### Wrong Gmail account
- Delete `token.pickle`
- Run with different Gmail account
- Browser will ask which account to use

## 📊 What Gets Analyzed

### Utility Analyzer
- Searches for: `bill OR statement OR invoice`
- Identifies: PSEG, Con Edison, Verizon Fios, etc.
- Extracts: Company name, service type, region, email count

### Telecom Analyzer
- Searches for: `from:verizon subject:(bill OR statement OR invoice)`
- Identifies: Verizon Fios (Internet) and Wireless (Mobile)
- Extracts: Service type, plan type, monthly billing amount

### AMEX Analyzer
- Searches for: American Express statements
- Identifies: Card type (Platinum, Gold, Blue), card ending digits
- Analyzes: Spending by category, estimated rewards points

## 💡 Pro Tips

1. **Test with utility analyzer first:**
   ```bash
   python orchestrator.py --utility --html
   ```

2. **Check the dashboard:**
   Open `reports/dashboard.html` in browser to see overview

3. **Review JSON output:**
   ```bash
   cat reports/aggregate_results.json | python -m json.tool
   ```

4. **Schedule automatic scanning:**
   - Create a cron job or scheduled task
   - Example: `0 9 * * 1` (Every Monday at 9 AM)
   - Or use the skill system in Cowork

## ✨ What's Next

Once Gmail is connected and first scan completes:
1. Review the generated HTML reports
2. Check `reports/aggregate_results.json` for detailed data
3. Optionally integrate with your dashboard or automation tools
4. Consider adding more analyzer types (bank statements, investment accounts, etc.)

## 📞 Support

If you encounter issues:
1. Check that `credentials.json` is in the correct location
2. Review error messages in terminal
3. Try deleting `token.pickle` and re-authenticating
4. Check Internet connection and Gmail account access

---

**Created**: March 8, 2026
**Project**: Financial Document Analyzer
**Status**: Ready for Gmail integration
