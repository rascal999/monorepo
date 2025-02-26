const runtime = {
  async handler(params, context = {}) {
    const { path, limit = 10 } = params;
    const { introspect = console.log } = context;

    try {
      // Validate required fields
      if (!path) {
        return "Missing required field: path (e.g., 'mangopay/appsec/security-tools')";
      }

      // Initialize axios within function scope
      const axios = require('axios');

      // Get credentials from runtime args or environment variables
      let GITLAB_HOST = (this.runtimeArgs || {}).GITLAB_HOST || process.env.GITLAB_HOST;
      let GITLAB_TOKEN = (this.runtimeArgs || {}).GITLAB_TOKEN || process.env.GITLAB_TOKEN;
      
      if (!GITLAB_HOST || !GITLAB_TOKEN) {
        return "Missing required GitLab credentials. Please configure them in the agent skills settings or environment variables.";
      }

      // Log thought process
      introspect(`Fetching git log for repository: ${path} (last ${limit} commits)`);

      // Initialize API client
      const api = axios.create({
        baseURL: `${GITLAB_HOST}/api/v4`,
        headers: { 'PRIVATE-TOKEN': GITLAB_TOKEN }
      });

      // Get repository commits
      const response = await api.get(`/projects/${encodeURIComponent(path)}/repository/commits`, {
        params: {
          per_page: limit,
          order_by: 'created_at',
          sort: 'desc'
        }
      });

      const commits = response.data;
      if (commits.length === 0) {
        return `No commits found in repository ${path}`;
      }

      // Format commit history
      const formattedCommits = commits.map(commit => ({
        id: commit.short_id,
        author: commit.author_name,
        date: new Date(commit.created_at).toLocaleString(),
        message: commit.message.split('\n')[0], // First line of commit message
        stats: commit.stats
      }));

      // Build response message
      let message = `Last ${commits.length} commits in ${path}:\n\n`;
      formattedCommits.forEach(commit => {
        message += `[${commit.id}] ${commit.date} by ${commit.author}\n`;
        message += `${commit.message}\n`;
        if (commit.stats) {
          message += `Files: +${commit.stats.additions} -${commit.stats.deletions}\n`;
        }
        message += '\n';
      });

      return message;

    } catch (error) {
      introspect(`Error fetching git log: ${error.message}`);
      if (error.response) {
        introspect(`GitLab API response: ${JSON.stringify(error.response.data || {}, null, 2)}`);
      }

      if (error.response?.status === 401) {
        return "Authentication failed. Please check your GitLab token.";
      } else if (error.response?.status === 404) {
        return "Repository not found. Please check the repository path.";
      }

      return `Failed to fetch git log: ${error.message}`;
    }
  }
};

module.exports = { runtime };