const runtime = {
  async handler(params, context = {}) {
    const { ticket, description } = params;
    const { introspect = console.log } = context;

    try {
      // Validate required fields
      if (!ticket || !description) {
        return "Missing required fields. Need both ticket key and description.";
      }

      // Initialize Jira client within function scope
      const JiraClient = require('jira-client');

      // Get credentials from runtime args
      const { JIRA_HOST, JIRA_EMAIL, JIRA_API_TOKEN } = this.runtimeArgs || {};
      if (!JIRA_HOST || !JIRA_EMAIL || !JIRA_API_TOKEN) {
        return "Missing required Jira credentials. Please configure them in the agent skills settings.";
      }

      // Log thought process
      introspect(`Updating description for Jira ticket ${ticket}`);

      // Initialize client
      const jira = new JiraClient({
        protocol: 'https',
        host: JIRA_HOST.replace('https://', '').replace('/', ''),
        username: JIRA_EMAIL,
        password: JIRA_API_TOKEN,
        apiVersion: '2',
        strictSSL: true
      });

      // Update the issue description
      await jira.updateIssue(ticket, {
        fields: {
          description: description
        }
      });

      // Return explicit success message
      return `Successfully updated Jira ticket description!\nTicket: ${ticket}\nURL: ${JIRA_HOST}/browse/${ticket}\n\nThe description has been updated with your specified text. No further action is needed.`;

    } catch (error) {
      introspect(`Error updating Jira ticket description: ${error.message}`);
      if (error.response) {
        introspect(`Jira API response: ${JSON.stringify(error.response.data || error.response.body || {}, null, 2)}`);
      }
      return `Failed to update ticket description: ${error.message}`;
    }
  }
};

module.exports = { runtime };