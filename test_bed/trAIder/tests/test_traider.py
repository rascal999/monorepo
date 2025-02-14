import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
import json
from app.stock_analyzer import StockAnalyzer
from app.consensus import ModelConsensus
from app.report import ReportGenerator
from app.utils import MODELS

@pytest.fixture
def mock_openai():
    with patch('openai.OpenAI') as mock:
        yield mock

@pytest.fixture
def stock_analyzer(mock_openai):
    return StockAnalyzer(model="gpt-3.5-turbo")

@pytest.fixture
def model_consensus():
    return ModelConsensus()

class TestStockAnalyzer:
    def test_analyze_stock_data(self, stock_analyzer, mock_openai):
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "recommendation": "buy",
            "stock": "LLOY.L",
            "confidence": 0.85,
            "reasoning": "Strong financial indicators"
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        result = stock_analyzer.analyze_stock_data("LLOY.L")
        
        assert isinstance(result, dict)
        assert "recommendation" in result
        assert "stock" in result
        assert "confidence" in result
        assert "reasoning" in result

class TestModelConsensus:
    def test_reach_consensus(self, model_consensus):
        analyses = [
            {
                "stock": "LLOY.L",
                "confidence": 0.85,
                "recommendation": "buy",
                "reasoning": "Strong financials",
                "model": "Model 1"
            },
            {
                "stock": "LLOY.L",
                "confidence": 0.75,
                "recommendation": "buy",
                "reasoning": "Positive outlook",
                "model": "Model 2"
            },
            {
                "stock": "VOD.L",
                "confidence": 0.90,
                "recommendation": "buy",
                "reasoning": "Market leader",
                "model": "Model 3"
            }
        ]

        consensus = model_consensus.reach_consensus(analyses)
        
        assert isinstance(consensus, list)
        assert len(consensus) <= 3  # Top 3 picks
        assert all(isinstance(pick, dict) for pick in consensus)
        assert all("stock" in pick for pick in consensus)
        assert all("confidence" in pick for pick in consensus)
        assert all("reasoning" in pick for pick in consensus)

class TestReportGenerator:
    def test_generate_html_report(self):
        consensus = [
            {
                "stock": "LLOY.L",
                "confidence": 0.85,
                "recommendation": "buy",
                "reasoning": "Model 1: Strong financials | Model 2: Positive outlook"
            }
        ]
        
        report_gen = ReportGenerator()
        html = report_gen.generate_html_report(consensus)
        
        assert isinstance(html, str)
        assert len(html) > 0
        
        # Parse HTML to ensure it's valid
        soup = BeautifulSoup(html, 'html.parser')
        assert soup.find('html') is not None
        assert soup.find('body') is not None
        assert soup.find('table') is not None
        
        # Check content
        assert "trAIder Stock Analysis Report" in html
        assert "LLOY.L" in html
        assert "Strong financials" in html