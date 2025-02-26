module.exports.runtime = {
  async handler(params, context = {}) {
    const { introspect = console.log } = context;

    try {
      // Get credentials from runtime args or environment variables
      let JIRA_HOST = (this.runtimeArgs || {}).JIRA_HOST || process.env.JIRA_HOST;
      let JIRA_EMAIL = (this.runtimeArgs || {}).JIRA_EMAIL || process.env.JIRA_EMAIL;
      let JIRA_API_TOKEN = (this.runtimeArgs || {}).JIRA_API_TOKEN || process.env.JIRA_API_TOKEN;
      
      if (!JIRA_HOST || !JIRA_EMAIL || !JIRA_API_TOKEN) {
        return "Missing required Jira credentials. Please configure them in the agent skills settings or environment variables.";
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
      introspect('Fetching list of Jira projects...');

      // Get all projects
      const projects = await jira.listProjects();

      if (!projects || projects.length === 0) {
        return "No projects found or you don't have access to any projects.";
      }

      // Format results
      const formattedProjects = projects.map(project => ({
        key: project.key,
        name: project.name,
        type: project.projectTypeKey || 'Unknown',
        lead: project.lead?.displayName || 'Unknown'
      }));

      // Build response message
      const message = [
        `Found ${formattedProjects.length} projects:`,
        ...formattedProjects.map(project => 
          `\n- ${project.key}: ${project.name}\n  Type: ${project.type} | Lead: ${project.lead}`
        )
      ].join('\n');

      return message;

    } catch (error) {
      introspect(`Error listing Jira projects: ${error.message}`);
      return `Failed to list Jira projects: ${error.message}`;
    }
  }
};