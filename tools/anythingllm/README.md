# AnythingLLM Docker Compose Setup

This directory contains a Docker Compose configuration for running AnythingLLM with proper permissions and secret management.

## Prerequisites

- Docker and Docker Compose installed
- Ollama running locally (for embeddings)
- OpenRouter API key (for LLM access)

## Setup

1. Run the setup script to prepare the directory structure and copy agent skills:

```bash
chmod +x setup.sh
./setup.sh
```

2. Start AnythingLLM:

```bash
docker-compose up -d
```

4. Access AnythingLLM at http://localhost:3001

## Configuration

The Docker Compose setup includes:

- Proper volume mounts for persistent storage
- Direct mounting of secrets from `/home/user/git/github/monorepo/secrets/environments/mgp/env`
- Automatic agent skills integration (copied on each container start)
- SSH key access for Git operations

## Troubleshooting

If you encounter permission issues:

```bash
chmod -R 777 storage
```

To view logs:

```bash
docker-compose logs -f
```

To restart the service:

```bash
docker-compose restart
```

## Updating

To update to the latest version:

```bash
docker-compose pull
docker-compose up -d