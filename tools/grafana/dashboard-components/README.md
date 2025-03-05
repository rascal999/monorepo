# Grafana Dashboard Components

This directory contains the components of the MongoDB SQLMap dashboard split into separate files for better maintainability.

## Directory Structure

- `dashboard-base.json` - Contains the base dashboard settings (annotations, time settings, etc.)
- `panels/` - Contains individual panel definitions
  - `panel-1-sqlmap-scans.json` - SQLMap Scans barchart
  - `panel-2-sqlmap-scan-details.json` - SQLMap Scan Details table
  - `panel-3-total-sqlmap-scans.json` - Total SQLMap Scans stat
  - `panel-4-http-methods.json` - HTTP Methods Distribution piechart
  - `panel-5-sqlmap-detailed-results.json` - SQLMap Detailed Results table
- `assemble-dashboard.py` - Script to assemble the components into a complete dashboard

## How to Use

### Modifying the Dashboard

1. To modify the base dashboard settings (title, time range, etc.), edit `dashboard-base.json`
2. To modify a specific panel, edit the corresponding file in the `panels/` directory
3. After making changes, run the assembly script to update the dashboard:

```bash
cd github/monorepo/tools/grafana
python3 dashboard-components/assemble-dashboard.py
```

### Adding a New Panel

1. Create a new JSON file in the `panels/` directory with a name like `panel-6-new-panel.json`
2. Define the panel configuration in the file
3. Run the assembly script to update the dashboard

### Removing a Panel

1. Delete the corresponding panel file from the `panels/` directory
2. Run the assembly script to update the dashboard

## Notes

- The panel IDs and positions are defined in each panel file
- The assembly script sorts panels by filename, so you can control the order by naming files appropriately
- The assembled dashboard is saved to `../data/dashboards/mongodb-dashboard.json`