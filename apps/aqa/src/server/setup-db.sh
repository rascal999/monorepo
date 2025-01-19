#!/bin/bash

# Create database
psql -U postgres -c "DROP DATABASE IF EXISTS aqa"
psql -U postgres -c "CREATE DATABASE aqa"

# Apply schema
psql -U postgres -d aqa -f schema.sql

# Load sample data
psql -U postgres -d aqa -f sample-data.sql

echo "Database setup complete!"
