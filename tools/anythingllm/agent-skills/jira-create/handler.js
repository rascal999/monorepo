const runtime = {
  async handler(params, context = {}) {
    const { project, type = "Task", summary, description } = params;
    const { introspect = console.log } = context;
    const callerId = `${this.config?.name || 'Jira Create Ticket'}-v${this.config?.version || '1.0.0'}`;

    try {
      // Validate required fields
      if (!project || !summary) {
        return "[JIRA CREATE RESPONSE] Missing required fields. Need at least project and summary.";
      }

      // Initialize Jira client within function scope
      const JiraClient = require('jira-client');

      // Get credentials from runtime args or environment variables
      let JIRA_HOST = (this.runtimeArgs || {}).JIRA_HOST || process.env.JIRA_HOST;
      let JIRA_EMAIL = (this.runtimeArgs || {}).JIRA_EMAIL || process.env.JIRA_EMAIL;
      let JIRA_API_TOKEN = (this.runtimeArgs || {}).JIRA_API_TOKEN || process.env.JIRA_API_TOKEN;
      
      if (!JIRA_HOST || !JIRA_EMAIL || !JIRA_API_TOKEN) {
        return "[JIRA CREATE RESPONSE] Missing required Jira credentials. Please configure them in the agent skills settings.";
      }

      // Log thought process
      introspect(`${callerId}: Creating Jira ticket in project ${project} with summary "${summary}"`);

      // Initialize client
      const jira = new JiraClient({
        protocol: 'https',
        host: JIRA_HOST.replace('https://', '').replace('/', ''),
        username: JIRA_EMAIL,
        password: JIRA_API_TOKEN,
        apiVersion: '2',
        strictSSL: true
      });

      // Prepare issue data
      const issueData = {
        fields: {
          project: {
            key: project
          },
          summary: summary,
          description: description || "No description provided",
          issuetype: {
            name: type
          }
        }
      };

      // Log the exact payload for debugging
      introspect(`${callerId}: Sending Jira payload: ${JSON.stringify(issueData, null, 2)}`);

      // Create the issue
      const issue = await jira.addNewIssue(issueData);

      if (!issue || !issue.key) {
        return "[JIRA CREATE RESPONSE] Failed to get issue key from Jira response";
      }

      // Return explicit success message with unique prefix
      return `[JIRA CREATE RESPONSE] ✅ Successfully created Jira ticket!

Ticket: ${issue.key}
URL: ${JIRA_HOST}/browse/${issue.key}

Summary: ${summary}
Type: ${type}
Project: ${project}

The ticket has been created with your specified details. No further action is needed.
Do not create additional tickets - this request has been completed.`;

    } catch (error) {
      introspect(`${callerId} error: ${error.message}`);
      if (error.response) {
        introspect(`Jira API response: ${JSON.stringify(error.response.data || error.response.body || {}, null, 2)}`);
      }
      return `[JIRA CREATE RESPONSE] ❌ Failed to create Jira ticket: ${error.message}`;
    }
  }
};

module.exports = { runtime };