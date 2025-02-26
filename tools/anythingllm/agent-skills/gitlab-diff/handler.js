const runtime = {
  async handler(params, context = {}) {
    const { path, hash } = params;
    const { introspect = console.log } = context;

    try {
      // Validate required fields
      if (!path || !hash) {
        return "Missing required fields. Need both repository path and commit hash.";
      }

      // Initialize axios within function scope
      const axios = require('axios');

      // Get credentials from runtime args
      const { GITLAB_HOST, GITLAB_TOKEN } = this.runtimeArgs || {};
      if (!GITLAB_HOST || !GITLAB_TOKEN) {
        return "Missing required GitLab credentials. Please configure them in the agent skills settings.";
      }

      // Log thought process
      introspect(`Fetching diff for commit ${hash} in repository: ${path}`);

      // Initialize API client
      const api = axios.create({
        baseURL: `${GITLAB_HOST}/api/v4`,
        headers: { 'PRIVATE-TOKEN': GITLAB_TOKEN }
      });

      // First get commit details
      const commitResponse = await api.get(
        `/projects/${encodeURIComponent(path)}/repository/commits/${hash}`
      );
      const commit = commitResponse.data;

      // Then get the diff
      const diffResponse = await api.get(
        `/projects/${encodeURIComponent(path)}/repository/commits/${hash}/diff`
      );
      const diffs = diffResponse.data;

      if (diffs.length === 0) {
        return `No changes found in commit ${hash}`;
      }

      // Format the response
      let message = `Commit Details:\n`;
      message += `Hash: ${commit.short_id}\n`;
      message += `Author: ${commit.author_name}\n`;
      message += `Date: ${new Date(commit.created_at).toLocaleString()}\n`;
      message += `Message: ${commit.message}\n\n`;
      message += `Changes (${diffs.length} files modified):\n\n`;

      diffs.forEach(diff => {
        message += `File: ${diff.new_path}\n`;
        if (diff.new_file) {
          message += `[New File]\n`;
        } else if (diff.deleted_file) {
          message += `[Deleted File]\n`;
        } else if (diff.renamed_file) {
          message += `[Renamed from: ${diff.old_path}]\n`;
        }
        
        // Add file stats
        message += `Changes: +${(diff.diff.match(/^\+/gm) || []).length} -${(diff.diff.match(/^-/gm) || []).length}\n`;
        
        // Format the diff output
        const formattedDiff = diff.diff
          .split('\n')
          .map(line => {
            if (line.startsWith('+')) return `\x1b[32m${line}\x1b[0m`; // Green for additions
            if (line.startsWith('-')) return `\x1b[31m${line}\x1b[0m`; // Red for deletions
            return line;
          })
          .join('\n');
        
        message += `\n${formattedDiff}\n\n`;
      });

      return message;

    } catch (error) {
      introspect(`Error fetching diff: ${error.message}`);
      if (error.response) {
        introspect(`GitLab API response: ${JSON.stringify(error.response.data || {}, null, 2)}`);
      }

      if (error.response?.status === 401) {
        return "Authentication failed. Please check your GitLab token.";
      } else if (error.response?.status === 404) {
        return "Repository or commit not found. Please check the repository path and commit hash.";
      }

      return `Failed to fetch diff: ${error.message}`;
    }
  }
};

module.exports = { runtime };