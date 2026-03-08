#!/usr/bin/env python3
"""
Unit tests for HTMLGenerator.

Tests:
- Environment setup
- Template rendering
- Filter registration and usage
- Context validation
- Error handling
- Template existence checks
"""

import os
import pytest
import tempfile
from pathlib import Path
from jinja2 import TemplateNotFound
from shared.html_generator import HTMLGenerator, create_default_templates


class TestHTMLGeneratorInitialization:
    """Test HTMLGenerator initialization."""

    def test_initialization_with_default_path(self):
        """Test initialization with default template directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            generator = HTMLGenerator()
            assert generator.template_dir == 'templates'
            assert generator.env is not None

    def test_initialization_with_custom_path(self):
        """Test initialization with custom template directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = os.path.join(tmpdir, 'custom_templates')
            os.makedirs(custom_path)
            generator = HTMLGenerator(template_dir=custom_path)
            assert generator.template_dir == custom_path


class TestFilterRegistration:
    """Test Jinja2 filter registration."""

    def test_format_currency_filter(self):
        """Test currency formatting filter."""
        generator = HTMLGenerator()
        
        # Test basic filtering
        html = generator.render_string(
            '{{ amount | format_currency }}',
            {'amount': 123.45}
        )
        assert '$123.45' in html

    def test_format_currency_with_commas(self):
        """Test currency formatting with thousands separator."""
        generator = HTMLGenerator()
        
        html = generator.render_string(
            '{{ amount | format_currency }}',
            {'amount': 1234.56}
        )
        assert '$1,234.56' in html

    def test_format_currency_none(self):
        """Test currency formatting with None."""
        generator = HTMLGenerator()
        
        html = generator.render_string(
            '{{ amount | format_currency }}',
            {'amount': None}
        )
        assert '$0.00' in html

    def test_format_percent_filter(self):
        """Test percentage formatting filter."""
        generator = HTMLGenerator()
        
        html = generator.render_string(
            '{{ ratio | format_percent }}',
            {'ratio': 0.75}
        )
        assert '75.0%' in html

    def test_format_percent_with_decimals(self):
        """Test percentage formatting with custom decimals."""
        generator = HTMLGenerator()
        
        html = generator.render_string(
            '{{ ratio | format_percent(2) }}',
            {'ratio': 0.333333}
        )
        assert '33.33%' in html

    def test_format_date_filter(self):
        """Test date formatting filter."""
        generator = HTMLGenerator()
        
        html = generator.render_string(
            '{{ date | format_date }}',
            {'date': '2026-03-08T10:30:00'}
        )
        assert '2026-03-08' in html


class TestContextValidation:
    """Test context validation."""

    def test_validate_context_valid(self):
        """Test validation of valid context."""
        generator = HTMLGenerator()
        
        context = {
            'timestamp': '2026-03-08',
            'total_emails': 50,
        }
        
        # Should not raise
        generator._validate_context(context)

    def test_validate_context_not_dict(self):
        """Test validation with non-dict context."""
        generator = HTMLGenerator()
        
        with pytest.raises(ValueError):
            generator._validate_context([1, 2, 3])

    def test_validate_context_missing_keys(self):
        """Test validation with missing required keys."""
        generator = HTMLGenerator()
        
        context = {'timestamp': '2026-03-08'}  # Missing total_emails
        
        with pytest.raises(ValueError) as exc_info:
            generator._validate_context(context)
        
        assert 'total_emails' in str(exc_info.value)


class TestTemplateRendering:
    """Test template rendering."""

    def test_render_string_basic(self):
        """Test rendering a simple template string."""
        generator = HTMLGenerator()
        
        template = "Hello {{ name }}!"
        context = {'name': 'World'}
        
        result = generator.render_string(template, context)
        assert result == 'Hello World!'

    def test_render_string_with_filters(self):
        """Test rendering with filters."""
        generator = HTMLGenerator()
        
        template = "Price: {{ price | format_currency }}"
        context = {'price': 99.99}
        
        result = generator.render_string(template, context)
        assert '$99.99' in result

    def test_render_string_with_loops(self):
        """Test rendering with loops."""
        generator = HTMLGenerator()
        
        template = """{% for item in items %}<li>{{ item }}</li>{% endfor %}"""
        context = {'items': ['A', 'B', 'C']}
        
        result = generator.render_string(template, context)
        assert '<li>A</li>' in result
        assert '<li>B</li>' in result
        assert '<li>C</li>' in result

    def test_render_template_file(self):
        """Test rendering an actual template file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test template
            template_path = os.path.join(tmpdir, 'test.html')
            with open(template_path, 'w') as f:
                f.write('<h1>{{ title }}</h1>')
            
            generator = HTMLGenerator(template_dir=tmpdir)
            result = generator.render('test.html', {
                'title': 'Test Page',
                'timestamp': '2026-03-08',
                'total_emails': 10,
            })
            
            assert '<h1>Test Page</h1>' in result

    def test_render_template_not_found(self):
        """Test rendering non-existent template."""
        generator = HTMLGenerator()
        
        with pytest.raises(TemplateNotFound):
            generator.render('nonexistent.html', {
                'timestamp': '2026-03-08',
                'total_emails': 10,
            })


class TestTemplateUtilities:
    """Test template utility methods."""

    def test_template_exists_true(self):
        """Test checking if existing template exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = os.path.join(tmpdir, 'exists.html')
            with open(template_path, 'w') as f:
                f.write('<p>Test</p>')
            
            generator = HTMLGenerator(template_dir=tmpdir)
            assert generator.template_exists('exists.html') is True

    def test_template_exists_false(self):
        """Test checking if non-existent template exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = HTMLGenerator(template_dir=tmpdir)
            assert generator.template_exists('nonexistent.html') is False

    def test_list_templates(self):
        """Test listing available templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test templates
            Path(os.path.join(tmpdir, 'template1.html')).write_text('<p>1</p>')
            Path(os.path.join(tmpdir, 'template2.html')).write_text('<p>2</p>')
            Path(os.path.join(tmpdir, 'readme.txt')).write_text('test')
            
            generator = HTMLGenerator(template_dir=tmpdir)
            templates = generator.list_templates()
            
            assert 'template1.html' in templates
            assert 'template2.html' in templates
            assert 'readme.txt' not in templates

    def test_save_html(self):
        """Test saving HTML to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = HTMLGenerator(template_dir=tmpdir)
            
            html = '<h1>Test</h1>'
            filepath = os.path.join(tmpdir, 'output', 'report.html')
            
            result = generator.save_html(html, filepath)
            
            assert os.path.exists(filepath)
            with open(filepath, 'r') as f:
                assert f.read() == html


class TestCreateDefaultTemplates:
    """Test default template creation."""

    def test_create_default_templates(self):
        """Test creation of default templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = os.path.join(tmpdir, 'templates')
            
            create_default_templates(template_dir)
            
            # Check that base template was created
            base_path = os.path.join(template_dir, '_base.html')
            assert os.path.exists(base_path)

    def test_create_default_templates_idempotent(self):
        """Test that creating default templates is idempotent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = os.path.join(tmpdir, 'templates')
            
            # Create templates twice
            create_default_templates(template_dir)
            original_mtime = os.path.getmtime(
                os.path.join(template_dir, '_base.html')
            )
            
            create_default_templates(template_dir)
            new_mtime = os.path.getmtime(
                os.path.join(template_dir, '_base.html')
            )
            
            # File should not have been modified
            assert original_mtime == new_mtime


class TestJinja2Integration:
    """Test Jinja2-specific features."""

    def test_autoescape_enabled(self):
        """Test that autoescape is enabled for security."""
        generator = HTMLGenerator()
        
        template = '<p>{{ content }}</p>'
        context = {'content': '<script>alert("xss")</script>'}
        
        result = generator.render_string(template, context)
        
        # Script tag should be escaped
        assert '&lt;script&gt;' in result
        assert '<script>' not in result

    def test_template_inheritance(self):
        """Test template inheritance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create base template
            base_path = os.path.join(tmpdir, '_base.html')
            with open(base_path, 'w') as f:
                f.write("""
<html>
<head><title>{% block title %}Default{% endblock %}</title></head>
<body>{% block content %}{% endblock %}</body>
</html>
                """)
            
            # Create child template
            child_path = os.path.join(tmpdir, 'child.html')
            with open(child_path, 'w') as f:
                f.write("""
{% extends "_base.html" %}
{% block title %}Custom{% endblock %}
{% block content %}<h1>Hello</h1>{% endblock %}
                """)
            
            generator = HTMLGenerator(template_dir=tmpdir)
            result = generator.render('child.html', {
                'timestamp': '2026-03-08',
                'total_emails': 10,
            })
            
            assert '<title>Custom</title>' in result
            assert '<h1>Hello</h1>' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
