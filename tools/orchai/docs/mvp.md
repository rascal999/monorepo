# OrchAI MVP Requirements

## Core Infrastructure

### 1. Docker Environment
- Base Docker setup with volume for git repos
- Docker-in-Docker capability for bot containers
- Shared volume mount points for repo access
- Command line access within containers for model-driven operations

### 2. Bot Configuration
- Basic YAML configuration structure in team/
- Required MVP bots:
  1. PM bot: Project coordination and requirement gathering
  2. Dev bot: Code implementation and repository management
- Configuration schema:
  ```yaml
  name: bot_name
  role: pm|dev
  model: openrouter_model_name
  permissions:
    - repo_access
    - docker_access
  ```

### 3. AI Integration
- OpenRouter API integration for both bots
- Model configurations:
  - PM Bot: Optimized for project management and requirement analysis
  - Dev Bot: Optimized for code generation and technical tasks
- Command execution capabilities:
  - Models can execute shell commands within their Docker containers
  - Access to development tools and utilities
  - Secure command execution environment

### 4. PM Bot Essential Features
- Monitor #general channel in Rocket.Chat
- Respond to any user messages
- Coordinate with Dev bot through direct mentions
- Use OpenRouter model for:
  - Requirement analysis
  - Task breakdown
  - Project coordination
- Basic requirement gathering flow:
  1. Project name
  2. Basic description
  3. Confirmation step
- Git repo creation capability
- Dev bot task coordination

### 5. Dev Bot Essential Features
- Read all messages in #general
- Respond only to PM bot mentions
- Use OpenRouter model for:
  - Code generation
  - Code review
  - Technical decision making
- Git operations:
  - Branch creation
  - Code implementation
  - Basic testing
- Docker container management for development
- Command line access for development tasks
- Report status back to PM bot

### 6. Communication Architecture
- All communication happens in #general channel
- Message handling rules:
  - PM bot can respond to any message from users or Dev bot
  - Dev bot:
    - Can read all messages in #general
    - Only responds when directly addressed by PM bot (@dev)
    - Ignores direct messages from users
- Basic response formatting

## MVP Flow

1. User posts requirement in #general
2. PM bot (via OpenRouter model) engages with user to gather details
3. PM bot creates git repository
4. PM bot delegates tasks to Dev bot via @mentions
5. Dev bot (via OpenRouter model) implements code and reports back to PM bot
6. PM bot relays progress/results back to user

## Technical Prerequisites

1. Docker Engine
2. Rocket.Chat server
3. Git server access
4. Storage volume for repositories
5. OpenRouter API access
6. Command line tools within containers

## Security Considerations

1. Docker volume isolation
2. Bot authentication
3. Repository access controls
4. Message authorization (ensuring Dev bot only responds to PM bot)
5. Secure model API access
6. Command execution restrictions

## Limitations

- Two bot system only (PM + Dev)
- Basic requirement gathering
- No QA bot integration yet
- Limited Docker-in-Docker functionality
- Basic repository management
- Restricted command execution environment

## Future Expansion Points

1. QA bot integration
2. Enhanced requirement gathering
3. Automated testing integration
4. Advanced Docker orchestration
5. Multi-repository management
6. Extended model capabilities
7. Advanced command line operations