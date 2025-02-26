const runtime = {
  async handler(params, context = {}) {
    const { ticket, includeComments = false } = params;
    const { introspect = console.log } = context;

    try {
      // Validate required fields
      if (!ticket) {
        return "Missing required field: ticket key";
      }

      // Initialize Jira client within function scope
      const JiraClient = require('jira-client');

      // Get credentials from runtime args
      const { JIRA_HOST, JIRA_EMAIL, JIRA_API_TOKEN } = this.runtimeArgs || {};
      if (!JIRA_HOST || !JIRA_EMAIL || !JIRA_API_TOKEN) {
        return "Missing required Jira credentials. Please configure them in the agent skills settings.";
      }

      // Log thought process
      introspect(`Fetching details for Jira ticket ${ticket}`);

      // Initialize client
      const jira = new JiraClient({
        protocol: 'https',
        host: JIRA_HOST.replace('https://', '').replace('/', ''),
        username: JIRA_EMAIL,
        password: JIRA_API_TOKEN,
        apiVersion: '2',
        strictSSL: true
      });

      // Get issue details
      const issue = await jira.findIssue(ticket);
      
      // Format response
      let response = `I've successfully retrieved the Jira ticket ${issue.key}. Here are the key details:\n\n`;
      
      // Title block
      response += `Title: ${issue.fields.summary}\n`;
      response += `Status: ${issue.fields.status.name}\n`;
      response += `Priority: ${issue.fields.priority?.name || 'Not set'}\n`;
      response += `Type: ${issue.fields.issuetype.name}\n\n`;

      // Key Details block
      response += 'Key Details:\n\n';
      response += `    Reporter: ${issue.fields.reporter.displayName}\n`;
      response += `    Assignee: ${issue.fields.assignee?.displayName || 'Unassigned'}\n`;
      response += `    Created: ${new Date(issue.fields.created).toLocaleString()}\n`;
      response += `    Last Updated: ${new Date(issue.fields.updated).toLocaleString()}\n\n`;

      // Description block
      if (issue.fields.description) {
        response += `Description: ${issue.fields.description}\n\n`;
      }

      // Get comments if requested
      if (includeComments && issue.fields.comment?.comments?.length > 0) {
        response += 'Comments:\n\n';
        issue.fields.comment.comments.forEach(comment => {
          response += `    ${comment.author.displayName} (${new Date(comment.created).toLocaleString()}):\n`;
          response += `    ${comment.body.replace(/\n/g, '\n    ')}\n\n`;
        });
      }

      response += `View ticket: ${JIRA_HOST}/browse/${issue.key}`;
      return response;

    } catch (error) {
      introspect(`Error fetching Jira ticket details: ${error.message}`);
      if (error.response) {
        introspect(`Jira API response: ${JSON.stringify(error.response.data || error.response.body || {}, null, 2)}`);
      }
      return `Failed to fetch ticket details: ${error.message}`;
    }
  }
};

module.exports = { runtime };