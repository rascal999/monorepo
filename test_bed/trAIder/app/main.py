#!/usr/bin/env python3
"""
trAIder main entry point
"""
from app.stock_analyzer import StockAnalyzer
from app.consensus import ModelConsensus
from app.report import ReportGenerator
from app.utils import MODELS, get_sample_stocks
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting trAIder analysis")
        
        # Initialize components
        analyzers = [StockAnalyzer(model) for model in MODELS]
        consensus_engine = ModelConsensus()
        report_generator = ReportGenerator()

        # Get a sample stock to trigger analysis
        # Each model will consider all FTSE stocks and return their best pick
        stocks = get_sample_stocks()
        trigger_stock = stocks[0]
        
        # Get each model's top FTSE stock pick
        model_picks = []
        for analyzer in analyzers:
            logger.info(f"Getting {analyzer.model}'s top FTSE stock pick...")
            analysis = analyzer.analyze_stock_data(trigger_stock)
            model_picks.append(analysis)
            logger.info(f"Model {analyzer.model} picked {analysis['stock']}: {analysis['recommendation']} (confidence: {analysis['confidence']})")
            logger.info(f"Reasoning: {analysis['reasoning']}")

        # Get consensus from model picks
        consensus_list = consensus_engine.reach_consensus(model_picks)
        if consensus_list:
            consensus = consensus_list[0]  # Get the first (highest confidence) consensus
            consensus['model'] = 'Consensus'  # Mark as consensus
            logger.info(f"Consensus recommendation: {consensus['recommendation']} (confidence: {consensus['confidence']})")
            logger.info(f"Consensus reasoning: {consensus['reasoning']}")
            
            # Add consensus to picks for the report
            model_picks.append(consensus)

        # Generate report
        logger.info("Generating report")
        report = report_generator.generate_html_report(model_picks)

        # Save report to workspace
        report_path = "/workspace/stock_analysis_report.html"
        with open(report_path, "w") as f:
            f.write(report)

        logger.info(f"Analysis complete. Report generated: {report_path}")

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
