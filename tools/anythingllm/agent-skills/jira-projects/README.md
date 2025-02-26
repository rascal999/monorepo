# Jira Projects Agent Skill

This agent skill allows you to list all accessible Jira projects in your instance.

## Setup

1. Get your Jira API token from https://id.atlassian.com/manage-profile/security/api-tokens
2. Configure the following settings in the agent skills configuration:
   - JIRA_HOST: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
   - JIRA_EMAIL: Your Jira account email
   - JIRA_API_TOKEN: Your Jira API token

## Usage

Simply ask the agent to list Jira projects. Example prompts:
- "List all Jira projects"
- "Show me my Jira projects"
- "What projects are in Jira?"

The agent will return a list of all projects you have access to, including:
- Project key
- Project name
- Project type
- Project lead

## Installation

1. Place this folder in your AnythingLLM agent-skills directory
2. Run `npm install` in this directory to install dependencies
3. Configure the required settings in the AnythingLLM UI
4. Restart your agent if it's already running