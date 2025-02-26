#!/bin/bash

# Create storage directory structure
mkdir -p storage/plugins/agent-skills storage/plugins/agent-flows storage/comkey storage/models/openrouter

# Set permissions
chmod -R 777 storage

# Copy agent skills to storage
cp -r agent-skills/* storage/plugins/agent-skills/ || echo "No agent skills to copy"

echo "Setup completed successfully!"