#!/usr/bin/env python3
import json
import os
import sys

# Define paths
COMPONENTS_DIR = os.path.dirname(os.path.abspath(__file__))
PANELS_DIR = os.path.join(COMPONENTS_DIR, "panels")
BASE_DASHBOARD_PATH = os.path.join(COMPONENTS_DIR, "dashboard-base.json")
OUTPUT_DASHBOARD_PATH = os.path.join(COMPONENTS_DIR, "..", "data", "dashboards", "mongodb-dashboard.json")

def main():
    # Load base dashboard
    with open(BASE_DASHBOARD_PATH, 'r') as f:
        dashboard = json.load(f)
    
    # Initialize panels array
    dashboard['panels'] = []
    
    # Load all panel files
    panel_files = sorted([f for f in os.listdir(PANELS_DIR) if f.endswith('.json')])
    
    for panel_file in panel_files:
        panel_path = os.path.join(PANELS_DIR, panel_file)
        with open(panel_path, 'r') as f:
            panel = json.load(f)
        
        # Add panel to dashboard
        dashboard['panels'].append(panel)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_DASHBOARD_PATH), exist_ok=True)
    
    # Write assembled dashboard to output file
    with open(OUTPUT_DASHBOARD_PATH, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"Dashboard assembled successfully: {OUTPUT_DASHBOARD_PATH}")

if __name__ == "__main__":
    main()