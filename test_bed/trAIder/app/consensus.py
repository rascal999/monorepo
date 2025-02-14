"""Consensus module for combining multiple model analyses"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ModelConsensus:
    def reach_consensus(self, analyses: List[Dict]) -> List[Dict]:
        """Determine consensus from multiple model analyses"""
        try:
            # Group analyses by stock
            stock_analyses = {}
            for analysis in analyses:
                stock = analysis["stock"]
                if stock not in stock_analyses:
                    stock_analyses[stock] = []
                stock_analyses[stock].append(analysis)

            # Calculate consensus for each stock
            consensus = []
            for stock, stock_analysis in stock_analyses.items():
                buy_confidence = sum(
                    a["confidence"] for a in stock_analysis 
                    if a["recommendation"] == "buy"
                )
                if buy_confidence > 0:
                    consensus.append({
                        "stock": stock,
                        "confidence": buy_confidence / len(stock_analysis),
                        "recommendation": "buy",
                        "reasoning": " | ".join(
                            f"{a['model'] if 'model' in a else 'Model'}: {a['reasoning']}" 
                            for a in stock_analysis
                        )
                    })

            # Sort by confidence and return top 3
            return sorted(
                consensus,
                key=lambda x: x["confidence"],
                reverse=True
            )[:3]
        except Exception as e:
            logger.error(f"Error reaching consensus: {str(e)}")
            return []