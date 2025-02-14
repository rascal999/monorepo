# trAIder

A sophisticated FTSE stock analysis tool that leverages multiple AI models through OpenRouter to reach a consensus on 24-hour stock picks.

## Overview

trAIder uses three powerful AI models to analyze FTSE 100 stocks and generate investment recommendations:
- OpenAI GPT-4 Turbo
- Anthropic Claude 3 Opus
- Google Gemini Pro

Each model independently:
1. Searches for current market data and news
2. Analyzes FTSE 100 stocks
3. Provides recommendations with confidence scores

The system then reaches a consensus on the top 3 picks for 24-hour holding periods.

## Features

- Multi-model analysis using OpenRouter API
- Web scraping for real-time market data
- Consensus-based decision making
- Confidence scoring system
- HTML report generation with detailed reasoning
- Automated FTSE 100 stock listing

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Copy `.env.example` to `.env` and add your OpenRouter API key:
```bash
cp .env.example .env
# Edit .env and add your API key
```

## Usage

Run the main script:
```bash
python -m app.traider
```

This will:
1. Fetch current FTSE 100 stock list
2. Analyze stocks using all three models
3. Generate a consensus report
4. Save the report as `stock_analysis_report.html`

## Testing

Run the test suite:
```bash
pytest tests/
```

For coverage report:
```bash
pytest --cov=app tests/
```

## Architecture

- `StockAnalyzer`: Individual model analysis
- `WebSearcher`: Market data collection
- `ModelConsensus`: Multi-model agreement
- `ReportGenerator`: HTML output generation

## Output

The HTML report includes:
- Top 3 stock recommendations
- Confidence scores
- Detailed reasoning from each model
- Timestamp of analysis
- Models used for analysis

## Notes

- Requires OpenRouter API key with access to specified models
- Web scraping respects rate limits and robots.txt
- Designed for 24-hour holding period analysis
- Not financial advice - use at your own risk

## License

MIT License
