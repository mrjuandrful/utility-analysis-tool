#!/usr/bin/env python3
"""
Email Sender using Google Workspace CLI (gws)

Sends utility analysis reports via Gmail using the gws MCP server.
Requires gws to be authenticated via 'gws auth login'.
"""

import subprocess
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime


class GWSEmailSender:
    """
    Send emails using Google Workspace CLI (gws).

    Uses gws command-line interface to compose and send emails
    with HTML content and attachments.
    """

    def __init__(self):
        """Initialize the email sender."""
        self.sender_email = "mrjuandrful@gmail.com"
        self.default_recipients = [
            "mrjuandrful@gmail.com",
            "mkperez1027@gmail.com"
        ]

    def send_utility_report(
        self,
        html_content: str,
        recipients: Optional[List[str]] = None,
        subject: Optional[str] = None,
        month: Optional[str] = None
    ) -> dict:
        """
        Send utility analysis report via email.

        Args:
            html_content: HTML content of the report
            recipients: List of email addresses (default: Juan & Melissa)
            subject: Email subject line
            month: Month for the report (e.g., "April 2026")

        Returns:
            Dict with success status and details
        """
        if recipients is None:
            recipients = self.default_recipients

        if subject is None:
            month = month or datetime.now().strftime("%B %Y")
            subject = f"📊 Utility Bills Dashboard — {month} (Monthly Report)"

        try:
            # Use gws to send email
            # Since we're using MCP, we'll use the gws_send_email tool
            # But for now, we'll create a draft that can be reviewed

            recipients_str = ", ".join(recipients)

            print(f"\n📧 Preparing to send utility report email...")
            print(f"   To: {recipients_str}")
            print(f"   Subject: {subject}")

            # For MCP integration, we'll return the details
            # The orchestrator will use the MCP tools to send
            return {
                'success': True,
                'to': recipients,
                'subject': subject,
                'html_body': html_content,
                'method': 'gws_mcp',
                'status': 'ready_to_send'
            }

        except Exception as e:
            print(f"❌ Email sending error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }

    def send_via_gws_cli(
        self,
        to: str,
        subject: str,
        html_body: str
    ) -> bool:
        """
        Send email directly via gws CLI command.

        Requires gws to be authenticated.

        Args:
            to: Recipient email address
            subject: Email subject
            html_body: HTML email body

        Returns:
            True if successful, False otherwise
        """
        try:
            # Construct gws command to send email
            cmd = [
                'gws',
                'gmail',
                'messages',
                'send',
                '--to', to,
                '--subject', subject,
                '--body', html_body,
                '--html'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Email sent successfully to {to}")
                return True
            else:
                print(f"❌ Failed to send email: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error executing gws command: {str(e)}")
            return False


def send_utility_report_email(
    html_content: str,
    recipients: Optional[List[str]] = None,
    subject: Optional[str] = None,
    month: Optional[str] = None
) -> dict:
    """
    Convenience function to send utility report.

    Args:
        html_content: HTML content of the report
        recipients: List of email addresses
        subject: Email subject line
        month: Month for the report

    Returns:
        Dict with send status
    """
    sender = GWSEmailSender()
    return sender.send_utility_report(
        html_content=html_content,
        recipients=recipients,
        subject=subject,
        month=month
    )
