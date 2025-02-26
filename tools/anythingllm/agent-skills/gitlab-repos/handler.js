const runtime = {
  async handler(params, context = {}) {
    const { path } = params;
    const { introspect = console.log } = context;

    try {
      // Validate required fields
      if (!path) {
        return "Missing required field: path (e.g., 'mangopay/appsec')";
      }

      // Initialize axios within function scope
      const axios = require('axios');

      // Get credentials from runtime args
      const { GITLAB_HOST, GITLAB_TOKEN } = this.runtimeArgs || {};
      if (!GITLAB_HOST || !GITLAB_TOKEN) {
        return "Missing required GitLab credentials. Please configure them in the agent skills settings.";
      }

      // Log thought process
      introspect(`Listing repositories for path: ${path}`);

      // Initialize API client
      const api = axios.create({
        baseURL: `${GITLAB_HOST}/api/v4`,
        headers: { 'PRIVATE-TOKEN': GITLAB_TOKEN }
      });

      // First try as a group
      try {
        const response = await api.get(`/groups/${encodeURIComponent(path)}/projects`);
        const repos = response.data.map(repo => ({
          name: repo.name,
          path: repo.path_with_namespace,
          description: repo.description || '',
          url: repo.web_url
        }));

        return `Found ${repos.length} repositories in ${path}:\n${repos.map(repo => 
          `- ${repo.name} (${repo.path})\n  ${repo.description}\n  URL: ${repo.url}`
        ).join('\n')}`;

      } catch (groupError) {
        // If not found as group, try as a project
        if (groupError.response?.status === 404) {
          const response = await api.get(`/projects/${encodeURIComponent(path)}`);
          const repo = response.data;
          return `Found project ${path}:\n- ${repo.name} (${repo.path_with_namespace})\n  ${repo.description || ''}\n  URL: ${repo.web_url}`;
        }
        throw groupError;
      }

    } catch (error) {
      introspect(`Error accessing GitLab: ${error.message}`);
      if (error.response) {
        introspect(`GitLab API response: ${JSON.stringify(error.response.data || {}, null, 2)}`);
      }

      if (error.response?.status === 401) {
        return "Authentication failed. Please check your GitLab token.";
      } else if (error.response?.status === 404) {
        return "Resource not found. Please check the group/repository path.";
      }

      return `Failed to access GitLab: ${error.message}`;
    }
  }
};

module.exports = { runtime };