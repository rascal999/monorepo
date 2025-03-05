#!/bin/bash

# Activate the virtual environment
source /opt/venv/bin/activate

# Start MongoDB API in the background
python /usr/local/bin/mongodb_api.py &

# Start Grafana
/run.sh