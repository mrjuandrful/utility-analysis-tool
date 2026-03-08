#!/usr/bin/env python3
"""
Integration tests for Financial Analyzer Orchestrator.

Tests:
- Orchestrator initialization
- Single analyzer execution
- Multi-analyzer coordination
- Result aggregation
- JSON export
- HTML dashboard generation
"""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from orchestrator import FinancialAnalyzerOrchestrator


class TestOrchestratorInitialization:
    """Test orchestrator initialization."""

    def test_initialization_default(self):
        """Test default initialization."""
        orch = FinancialAnalyzerOrchestrator()
        assert orch.export_html is False
        assert orch.export_json is True
        assert len(orch.analyzers) == 3
        assert 'utility' in orch.analyzers
        assert 'telecom' in orch.analyzers
        assert 'amex' in orch.analyzers

    def test_initialization_with_html(self):
        """Test initialization with HTML export."""
        orch = FinancialAnalyzerOrchestrator(export_html=True)
        assert orch.export_html is True


class TestAnalyzerCoordination:
    """Test coordination of multiple analyzers."""

    def test_run_specific_single_analyzer(self):
        """Test running a single specific analyzer."""
        orch = FinancialAnalyzerOrchestrator()
        
        # Mock analyzer run methods
        orch.analyzers['utility'].run = Mock(return_value={
            'success': True,
            'data': {},
            'parsed_data': {'utilities_found': {}, 'total_utility_emails': 0}
        })
        
        result = orch.run_specific(['utility'])
        
        assert result['success'] is True
        assert 'utility' in result['results']

    def test_run_specific_multiple_analyzers(self):
        """Test running multiple specific analyzers."""
        orch = FinancialAnalyzerOrchestrator()
        
        # Mock analyzer runs
        for name in ['utility', 'telecom']:
            orch.analyzers[name].run = Mock(return_value={
                'success': True,
                'data': {},
                'parsed_data': {}
            })
        
        result = orch.run_specific(['utility', 'telecom'])
        
        assert result['success'] is True
        assert 'utility' in result['results']
        assert 'telecom' in result['results']


class TestResultAggregation:
    """Test aggregation of results from multiple analyzers."""

    def test_aggregate_results_structure(self):
        """Test aggregated results structure."""
        orch = FinancialAnalyzerOrchestrator()
        
        # Mock analyzer data
        orch.results = {
            'utility': {
                'success': True,
                'parsed_data': {
                    'utilities_found': {'PSEG': {}},
                    'total_utility_emails': 5
                }
            },
            'telecom': {
                'success': True,
                'parsed_data': {
                    'bills_found': {'Verizon Fios': {}},
                    'total_bills': 3
                }
            },
            'amex': {
                'success': True,
                'parsed_data': {
                    'total_spent': 1500.00,
                    'total_transactions': 25
                }
            }
        }
        
        # Mock analyzer total_emails
        orch.analyzers['utility'].total_emails = 50
        orch.analyzers['telecom'].total_emails = 45
        orch.analyzers['amex'].total_emails = 30
        
        aggregated = orch._aggregate_results()
        
        assert 'timestamp' in aggregated
        assert 'utility' in aggregated
        assert 'telecom' in aggregated
        assert 'amex' in aggregated
        assert 'summary' in aggregated

    def test_extract_utility_data(self):
        """Test utility data extraction."""
        orch = FinancialAnalyzerOrchestrator()
        orch.results = {
            'utility': {
                'success': True,
                'parsed_data': {
                    'utilities_found': {'PSEG': {'emails': 2}},
                    'total_utility_emails': 5
                }
            }
        }
        orch.analyzers['utility'].total_emails = 50
        
        data = orch._extract_utility_data()
        
        assert data['total_emails'] == 50
        assert data['utility_emails'] == 5
        assert 'utilities_found' in data

    def test_generate_summary(self):
        """Test summary generation."""
        orch = FinancialAnalyzerOrchestrator()
        
        # Set up analyzers with mock data
        orch.analyzers['utility'].total_emails = 50
        orch.analyzers['telecom'].total_emails = 45
        orch.analyzers['amex'].total_emails = 30
        
        orch.results = {
            'utility': {'success': True},
            'telecom': {'success': True},
            'amex': {'success': False}
        }
        
        summary = orch._generate_summary()
        
        assert summary['total_emails_analyzed'] == 125
        assert summary['analyzers_run'] == 2  # utility and telecom succeeded


class TestExports:
    """Test data export functionality."""

    def test_export_aggregate_json(self):
        """Test JSON export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            orch = FinancialAnalyzerOrchestrator()
            orch.aggregated_data = {
                'utility': {'utilities_found': {}},
                'telecom': {'bills_found': {}},
                'amex': {'total_spent': 1500.00}
            }
            
            filepath = orch._export_aggregate_json()
            
            assert os.path.exists(filepath)
            
            # Verify JSON content
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            assert 'utility' in data
            assert 'telecom' in data
            assert 'amex' in data

    def test_dashboard_html_generation(self):
        """Test HTML dashboard generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            orch = FinancialAnalyzerOrchestrator()
            orch.aggregated_data = {
                'utility': {
                    'utilities_found': {'PSEG': {}},
                    'utility_emails': 5,
                    'total_emails': 50
                },
                'telecom': {
                    'bills_found': {'Verizon': {}},
                    'bill_emails': 3,
                    'total_emails': 45
                },
                'amex': {
                    'statements': 6,
                    'total_spending': 1500.00,
                    'total_emails': 30
                },
                'summary': {
                    'total_emails_analyzed': 125,
                    'analyzers_run': 3,
                    'analysis_timestamp': '2026-03-08'
                }
            }
            
            filepath = orch._generate_master_dashboard()
            
            assert os.path.exists(filepath)
            
            # Verify HTML content
            with open(filepath, 'r') as f:
                html = f.read()
            
            assert '<!DOCTYPE html>' in html
            assert 'Financial Analysis Master Dashboard' in html
            assert 'Utility Companies' in html
            assert 'Telecom Services' in html
            assert 'Credit Card' in html


class TestCLI:
    """Test CLI functionality."""

    def test_list_analyzers(self, capsys):
        """Test listing available analyzers."""
        orch = FinancialAnalyzerOrchestrator()
        orch.list_analyzers()
        
        captured = capsys.readouterr()
        assert 'Available Analyzers' in captured.out
        assert 'Utility' in captured.out or 'utility' in captured.out.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
