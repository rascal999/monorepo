module.exports.runtime = {
  async handler(params, context = {}) {
    const { jql } = params;
    const { introspect = console.log } = context;

    try {
      // Validate required credentials
      const { JIRA_HOST, JIRA_EMAIL, JIRA_API_TOKEN } = this.runtimeArgs || {};
      if (!JIRA_HOST || !JIRA_EMAIL || !JIRA_API_TOKEN) {
        return "Missing required Jira credentials. Please configure them in the agent skills settings.";
      }

      // Initialize Jira client within function scope as recommended
      const JiraClient = require('./node_modules/jira-client');
      const jira = new JiraClient({
        protocol: 'https',
        host: JIRA_HOST.replace('https://', ''),
        username: JIRA_EMAIL,
        password: JIRA_API_TOKEN,
        apiVersion: '2',
        strictSSL: true
      });

      // Log thought process
      introspect(`Searching Jira with JQL: ${jql}`);

      // Search issues using JQL
      const searchResults = await jira.searchJira(jql, {
        maxResults: 10,  // Limit results to prevent overwhelming responses
        fields: ['key', 'summary', 'status', 'priority', 'assignee']
      });

      if (!searchResults.issues || searchResults.issues.length === 0) {
        return "No issues found matching the search criteria.";
      }

      // Format results
      const formattedIssues = searchResults.issues.map(issue => ({
        key: issue.key,
        summary: issue.fields.summary,
        status: issue.fields.status?.name || 'Unknown',
        priority: issue.fields.priority?.name || 'Unknown',
        assignee: issue.fields.assignee?.displayName || 'Unassigned'
      }));

      // Build response message
      const message = [
        `Found ${formattedIssues.length} issues:`,
        ...formattedIssues.map(issue => 
          `\n- ${issue.key}: ${issue.summary}\n  Status: ${issue.status} | Priority: ${issue.priority} | Assignee: ${issue.assignee}`
        )
      ].join('\n');

      return message;

    } catch (error) {
      introspect(`Error searching Jira: ${error.message}`);
      return `Failed to search Jira: ${error.message}`;
    }
  }
};