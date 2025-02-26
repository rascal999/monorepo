const channelCache = require('./channel-cache');
const loadSecrets = require('../utils/load-secrets');

const runtime = {
  async handler(params, context = {}) {
    const { channel } = params;
    const { introspect = console.log } = context;
    const callerId = `${this.config?.name || 'Slack Channel Reader'}-v${this.config?.version || '1.0.0'}`;

    // Debug: Log tool selection and parameters
    introspect('=== Slack Channel Reader Tool Selected ===');
    introspect('Parameters:', JSON.stringify(params, null, 2));

    try {
      // Validate required fields
      if (!channel) {
        introspect('Error: Missing channel parameter');
        return "Missing required field: channel (e.g., 'security')";
      }

      // Initialize Slack client within function scope
      const { WebClient } = require('@slack/web-api');

      // Get credentials from runtime args or from secrets
      let credentials = this.runtimeArgs || {};
      
      // If credentials are not in runtimeArgs, get them from secrets
      if (!credentials.SLACK_TOKEN) {
        // Get the skill ID from the config
        const skillId = this.config?.hubId || 'slack-channel-reader';
        
        // Get secrets for this skill
        const skillSecrets = loadSecrets.getSecretsForSkill(skillId);
        
        // Merge secrets with credentials
        credentials = {
          ...skillSecrets,
          ...credentials
        };
      }
      
      const { SLACK_TOKEN } = credentials;
      
      if (!SLACK_TOKEN) {
        introspect('Error: Missing Slack token');
        return "Missing required Slack token. Please configure it in the agent skills settings.";
      }

      // Log thought process
      introspect(`${callerId} fetching messages from #${channel}`);

      // Initialize client
      const slack = new WebClient(SLACK_TOKEN);

      // Get all channels with pagination if cache is stale
      async function getAllChannels() {
        let allChannels = [];
        let cursor;

        do {
          const response = await slack.conversations.list({
            limit: 1000,
            cursor: cursor,
            types: 'public_channel,private_channel'
          });

          if (!response.ok) {
            throw new Error(response.error || 'Failed to list channels');
          }

          allChannels = allChannels.concat(response.channels);
          cursor = response.response_metadata?.next_cursor;
        } while (cursor);

        return allChannels;
      }

      // Check if we need to refresh the channel cache
      const isStale = await channelCache.isStale();
      if (isStale) {
        introspect('Channel cache is stale or missing, refreshing...');
        const channels = await getAllChannels();
        await channelCache.save(channels);
        introspect(`Updated channel cache with ${channels.length} channels`);
      } else {
        introspect('Using existing channel cache');
      }

      // Get channel info from cache
      const channelInfo = await channelCache.getChannel(channel);
      if (!channelInfo) {
        introspect(`Channel #${channel} not found in cache`);
        return `Channel #${channel} not found`;
      }
      introspect(`Found channel #${channel} (ID: ${channelInfo.id})`);

      // Fetch messages (default 50)
      introspect(`Fetching messages from channel ID ${channelInfo.id}`);
      const messagesResult = await slack.conversations.history({
        channel: channelInfo.id,
        limit: 50
      });
      if (!messagesResult.ok) {
        throw new Error(messagesResult.error || 'Failed to fetch messages');
      }

      const messages = messagesResult.messages;
      if (messages.length === 0) {
        introspect(`No messages found in #${channel}`);
        return `No messages found in #${channel}`;
      }
      introspect(`Found ${messages.length} messages`);

      // Get user info for all unique users
      const userIds = [...new Set(messages.map(msg => msg.user))];
      introspect(`Fetching info for ${userIds.length} unique users`);
      const usersResult = await slack.users.list();
      if (!usersResult.ok) {
        throw new Error(usersResult.error || 'Failed to fetch user info');
      }

      const userMap = usersResult.members.reduce((acc, user) => {
        acc[user.id] = user.real_name || user.name;
        return acc;
      }, {});
      introspect('User info fetched successfully');

      // Format messages
      let response = `Here are the last ${messages.length} messages from #${channel}:\n\n`;
      messages.reverse().forEach(msg => {
        const userName = userMap[msg.user] || 'Unknown User';
        const timestamp = new Date(msg.ts * 1000).toLocaleString();
        const text = msg.text.replace(/\n/g, '\n  '); // Indent newlines for readability

        response += `[${timestamp}] ${userName}:\n  ${text}\n\n`;

        // Add info about threads if present
        if (msg.reply_count) {
          response += `  (${msg.reply_count} replies in thread)\n\n`;
        }

        // Add info about reactions if present
        if (msg.reactions && msg.reactions.length > 0) {
          const reactions = msg.reactions
            .map(r => `${r.name}: ${r.count}`)
            .join(', ');
          response += `  Reactions: ${reactions}\n\n`;
        }
      });

      introspect('Message formatting complete');
      return response;

    } catch (error) {
      introspect(`${callerId} error: ${error.message}`);
      if (error.response) {
        introspect(`Slack API response: ${JSON.stringify(error.response.data || {}, null, 2)}`);
      }

      if (error.response?.status === 401) {
        return "Authentication failed. Please check your Slack token.";
      }

      return `Failed to fetch messages: ${error.message}`;
    }
  }
};

module.exports = { runtime };