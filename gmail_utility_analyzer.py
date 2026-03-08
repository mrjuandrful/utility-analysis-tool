#!/usr/bin/env python3
"""
Backwards Compatibility Wrapper for Gmail Utility Analyzer

This module provides backwards compatibility for code that imports from the root
level. New code should import from analyzers.gmail_utility_analyzer instead.

Migration path:
  OLD: from gmail_utility_analyzer import GmailUtilityAnalyzer
  NEW: from analyzers.gmail_utility_analyzer import GmailUtilityAnalyzer
"""

# Re-export the refactored analyzer for backwards compatibility
from analyzers.gmail_utility_analyzer import GmailUtilityAnalyzer, main, UTILITY_COMPANIES

__all__ = ['GmailUtilityAnalyzer', 'main', 'UTILITY_COMPANIES']
