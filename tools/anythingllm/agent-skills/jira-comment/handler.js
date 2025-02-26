const runtime = {
  async handler(params, context = {}) {
    const { ticket, comment } = params;
    const { introspect = console.log } = context;

    try {
      // Validate required fields
      if (!ticket || !comment) {
        return "Missing required fields. Need both ticket key and comment text.";
      }

      // Initialize Jira client within function scope
      const JiraClient = require('jira-client');

      // Get credentials from runtime args
      const { JIRA_HOST, JIRA_EMAIL, JIRA_API_TOKEN } = this.runtimeArgs || {};
      if (!JIRA_HOST || !JIRA_EMAIL || !JIRA_API_TOKEN) {
        return "Missing required Jira credentials. Please configure them in the agent skills settings.";
      }

      // Log thought process
      introspect(`Adding comment to Jira ticket ${ticket}`);

      // Initialize client
      const jira = new JiraClient({
        protocol: 'https',
        host: JIRA_HOST.replace('https://', '').replace('/', ''),
        username: JIRA_EMAIL,
        password: JIRA_API_TOKEN,
        apiVersion: '2',
        strictSSL: true
      });

      // Add the comment
      await jira.addComment(ticket, comment);

      // Return explicit success message
      return `Successfully added comment to Jira ticket!\nTicket: ${ticket}\nURL: ${JIRA_HOST}/browse/${ticket}\n\nThe comment has been added to the ticket. No further action is needed.`;

    } catch (error) {
      introspect(`Error adding comment to Jira ticket: ${error.message}`);
      if (error.response) {
        introspect(`Jira API response: ${JSON.stringify(error.response.data || error.response.body || {}, null, 2)}`);
      }
      return `Failed to add comment: ${error.message}`;
    }
  }
};

module.exports = { runtime };