#!/bin/bash

# Create necessary directories
mkdir -p /storage/plugins/agent-skills /storage/plugins/agent-flows /storage/comkey /storage/models/openrouter

# Create database file
touch /storage/anythingllm.db

# Set permissions
chmod -R 777 /storage

# Create JWT secret if it doesn't exist
if [ ! -f /storage/jwt_secret ]; then
  head -c 32 /dev/urandom | base64 > /storage/jwt_secret
fi
chmod 666 /storage/jwt_secret

# Copy agent skills
cp -r /agent-skills/* /storage/plugins/agent-skills/ || echo 'No agent skills to copy'

# Install dependencies for each agent skill
for d in /storage/plugins/agent-skills/*/; do
  if [ -f "${d}package.json" ]; then
    echo "Installing dependencies for $(basename $d)"
    cd "$d" && npm install
  fi
done