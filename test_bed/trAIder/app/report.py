"""Report generation module for stock analysis results"""
from datetime import datetime
from typing import List, Dict
from jinja2 import Template
from app.utils import MODELS

class ReportGenerator:
    def generate_html_report(self, analyses: List[Dict]) -> str:
        """Generate HTML report from analysis data"""
        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>trAIder Stock Analysis Report</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px;
                    line-height: 1.6;
                }
                table { 
                    border-collapse: collapse; 
                    width: 100%;
                    margin: 20px 0;
                }
                th, td { 
                    border: 1px solid #ddd; 
                    padding: 12px; 
                    text-align: left; 
                }
                th { 
                    background-color: #f5f5f5;
                    font-weight: bold;
                }
                .confidence-high { 
                    color: #28a745;
                    font-weight: bold;
                }
                .confidence-medium {
                    color: #ffc107;
                    font-weight: bold;
                }
                .header {
                    border-bottom: 2px solid #eee;
                    margin-bottom: 30px;
                }
                .footer {
                    margin-top: 30px;
                    color: #666;
                    font-size: 0.9em;
                }
                .bullet-list {
                    margin: 0;
                    padding-left: 20px;
                }
                .upsides {
                    color: #28a745;
                }
                .downsides {
                    color: #dc3545;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>trAIder Stock Analysis Report</h1>
                <p>Generated on: {{ timestamp }}</p>
            </div>
            
            <h2>Model Recommendations</h2>
            <table>
                <tr>
                    <th>Model</th>
                    <th>Stock</th>
                    <th>Recommendation</th>
                    <th>Confidence</th>
                    <th>Analysis</th>
                    <th>Upsides</th>
                    <th>Downsides</th>
                </tr>
                {% for analysis in analyses %}
                <tr>
                    <td>{{ analysis.model if 'model' in analysis else 'Consensus' }}</td>
                    <td><strong>{{ analysis.stock }}</strong></td>
                    <td>{{ analysis.recommendation }}</td>
                    <td class="{% if analysis.confidence >= 0.8 %}confidence-high{% else %}confidence-medium{% endif %}">
                        {{ "%.2f"|format(analysis.confidence) }}
                    </td>
                    <td>{{ analysis.reasoning }}</td>
                    <td>
                        <ul class="bullet-list upsides">
                        {% for point in analysis.upsides %}
                            <li>{{ point }}</li>
                        {% endfor %}
                        </ul>
                    </td>
                    <td>
                        <ul class="bullet-list downsides">
                        {% for point in analysis.downsides %}
                            <li>{{ point }}</li>
                        {% endfor %}
                        </ul>
                    </td>
                </tr>
                {% endfor %}
            </table>

            <div class="footer">
                <p>Analysis performed using OpenRouter AI models:</p>
                <ul>
                {% for model in models %}
                    <li>{{ model }}</li>
                {% endfor %}
                </ul>
            </div>
        </body>
        </html>
        """)

        return template.render(
            analyses=analyses,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            models=MODELS
        )
