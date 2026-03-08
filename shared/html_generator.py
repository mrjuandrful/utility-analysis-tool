#!/usr/bin/env python3
"""
HTML Report Generator using Jinja2 Templates

Provides a flexible, reusable system for generating professional HTML reports
using Jinja2 templates. Supports different report types (utility, telecom, amex)
with consistent styling and structure.

Usage:
    generator = HTMLGenerator()
    html = generator.render('utility_report.html', {
        'total_emails': 50,
        'utilities_found': {...},
        'timestamp': '2026-03-08',
    })
"""

import os
from pathlib import Path
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class HTMLGenerator:
    """
    Generates HTML reports from Jinja2 templates.

    Features:
    - Template environment setup with FileSystemLoader
    - Context validation and enrichment
    - Filter and helper function registration
    - Support for multiple report types
    - Error handling with helpful messages
    """

    def __init__(self, template_dir: str = 'templates'):
        """
        Initialize the HTML generator.

        Args:
            template_dir: Directory containing .html templates (default: 'templates')
        """
        self.template_dir = template_dir
        self.env = self._setup_environment()

    def _setup_environment(self) -> Environment:
        """
        Set up Jinja2 environment with filters and globals.

        Returns:
            Configured Jinja2 Environment object
        """
        # Create environment with template directory
        env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True,  # Auto-escape HTML for security
            trim_blocks=True,  # Remove block tags from output
            lstrip_blocks=True,  # Strip leading spaces
        )

        # Register custom filters
        env.filters['format_currency'] = self._filter_format_currency
        env.filters['format_percent'] = self._filter_format_percent
        env.filters['format_date'] = self._filter_format_date

        # Register custom globals
        env.globals['now'] = self._get_now

        return env

    def render(
        self,
        template_name: str,
        context: Dict,
        validate: bool = True
    ) -> str:
        """
        Render a template with the given context.

        Args:
            template_name: Name of template file (e.g., 'utility_report.html')
            context: Dict of variables to pass to template
            validate: Whether to validate context (default: True)

        Returns:
            Rendered HTML string

        Raises:
            TemplateNotFound: If template doesn't exist
            ValueError: If context is invalid (when validate=True)
        """
        if validate:
            self._validate_context(context)

        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound as e:
            raise TemplateNotFound(
                f"Template '{template_name}' not found in '{self.template_dir}'"
            )

    def render_string(self, template_string: str, context: Dict) -> str:
        """
        Render a template string directly (not from file).

        Useful for testing or dynamic templates.

        Args:
            template_string: Jinja2 template as string
            context: Dict of variables to pass to template

        Returns:
            Rendered HTML string
        """
        template = self.env.from_string(template_string)
        return template.render(**context)

    def _validate_context(self, context: Dict) -> None:
        """
        Validate that context dict is valid.

        Args:
            context: Dict to validate

        Raises:
            ValueError: If context is invalid
        """
        if not isinstance(context, dict):
            raise ValueError(f"Context must be a dict, got {type(context)}")

        # Ensure required keys are present
        required_keys = ['timestamp', 'total_emails']
        missing_keys = [k for k in required_keys if k not in context]
        if missing_keys:
            raise ValueError(f"Missing required context keys: {missing_keys}")

    # ==================== FILTERS ====================

    @staticmethod
    def _filter_format_currency(value) -> str:
        """
        Format a number as currency.

        Usage in template: {{ amount | format_currency }}
        """
        if value is None:
            return '$0.00'
        try:
            return f'${float(value):,.2f}'
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _filter_format_percent(value, decimals: int = 1) -> str:
        """
        Format a number as percentage.

        Usage in template: {{ ratio | format_percent }}
                          {{ ratio | format_percent(2) }}
        """
        if value is None:
            return '0%'
        try:
            return f'{float(value):.{decimals}f}%'
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _filter_format_date(value, format: str = '%Y-%m-%d') -> str:
        """
        Format a date string.

        Usage in template: {{ date_str | format_date }}
                          {{ date_str | format_date('%m/%d/%Y') }}
        """
        if value is None:
            return ''
        # Simple string slicing for standard format
        if format == '%Y-%m-%d' and isinstance(value, str) and len(value) >= 10:
            return value[:10]
        return str(value)

    # ==================== GLOBALS ====================

    @staticmethod
    def _get_now() -> str:
        """
        Get current timestamp.

        Usage in template: {{ now }}
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # ==================== UTILITY METHODS ====================

    def list_templates(self) -> list:
        """
        List all available templates in the template directory.

        Returns:
            List of template filenames
        """
        if not os.path.exists(self.template_dir):
            return []

        return [
            f for f in os.listdir(self.template_dir)
            if f.endswith('.html')
        ]

    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template exists.

        Args:
            template_name: Name of template to check

        Returns:
            True if template exists
        """
        try:
            self.env.get_template(template_name)
            return True
        except TemplateNotFound:
            return False

    def save_html(self, html: str, filepath: str) -> str:
        """
        Save HTML string to file.

        Args:
            html: HTML string to save
            filepath: Path to save to

        Returns:
            Filepath of saved file
        """
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        return filepath


# ==================== REPORT TYPE TEMPLATES ====================

DEFAULT_BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Financial Analysis Report{% endblock %}</title>
    <style>
        {% block styles %}
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f0f4f8;
            color: #1a1a2e;
        }
        header {
            background: linear-gradient(135deg, #1F4E79 0%, #2E75B6 100%);
            color: white;
            padding: 28px 40px;
        }
        header h1 { font-size: 1.7rem; font-weight: 700; }
        header p { font-size: 0.95rem; opacity: 0.85; margin-top: 6px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 28px 24px; }
        {% endblock %}
    </style>
</head>
<body>
    <header>
        <h1>{% block header_title %}Financial Analysis Report{% endblock %}</h1>
        <p>{% block header_subtitle %}Document Analysis Results{% endblock %}</p>
    </header>
    <div class="container">
        {% block content %}
        <p>No content provided.</p>
        {% endblock %}
    </div>
</body>
</html>
"""


def create_default_templates(template_dir: str = 'templates') -> None:
    """
    Create default template files if they don't exist.

    Creates base templates for utility, telecom, and amex reports.

    Args:
        template_dir: Directory to create templates in
    """
    os.makedirs(template_dir, exist_ok=True)

    # Create base template if it doesn't exist
    base_path = os.path.join(template_dir, '_base.html')
    if not os.path.exists(base_path):
        with open(base_path, 'w') as f:
            f.write(DEFAULT_BASE_TEMPLATE)


if __name__ == '__main__':
    # Create default templates
    create_default_templates()
    print("✅ Default templates created in 'templates/' directory")
