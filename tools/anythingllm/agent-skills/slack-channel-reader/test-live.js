const { runtime } = require('./handler');
const { WebClient } = require('@slack/web-api');
const channelCache = require('./channel-cache');

// Get plugin configuration
const pluginConfig = require('./plugin.json');
const SLACK_TOKEN = pluginConfig.setup_args.SLACK_TOKEN.value;

async function getAllChannels(slack) {
  let allChannels = [];
  let cursor;

  do {
    const response = await slack.conversations.list({
      limit: 1000,
      cursor: cursor,
      types: 'public_channel,private_channel'
    });

    if (!response.ok) {
      throw new Error('Failed to list channels');
    }

    allChannels = allChannels.concat(response.channels);
    cursor = response.response_metadata?.next_cursor;
  } while (cursor);

  return allChannels;
}

async function testSlackReader() {
  console.log('Testing Slack Channel Reader with live token...\n');

  // Set up runtime args
  runtime.runtimeArgs = {
    SLACK_TOKEN
  };

  // Test context
  const context = {
    introspect: console.log
  };

  try {
    // Initialize Slack client
    const slack = new WebClient(SLACK_TOKEN);

    // Check if we need to refresh the channel cache
    const isStale = await channelCache.isStale();
    if (isStale) {
      console.log('Channel cache is stale or missing, refreshing...');
      const channels = await getAllChannels(slack);
      await channelCache.save(channels);
      console.log(`Updated channel cache with ${channels.length} channels`);
    }

    // Get channels from cache
    const channels = await channelCache.getAllChannels();
    console.log(`Loaded ${channels.length} channels from cache.\n`);

    // Log all channels to help debug
    console.log('Available channels:');
    channels.forEach(ch => {
      console.log(`- #${ch.name} (${ch.id})`);
    });
    console.log('\n');

    // Find specific channels for testing
    const securityChannel = await channelCache.getChannel('security');
    const generalChannel = await channelCache.getChannel('general');

    console.log('Target channels:');
    console.log('security:', securityChannel ? `found (${securityChannel.id})` : 'not found');
    console.log('general:', generalChannel ? `found (${generalChannel.id})` : 'not found');
    console.log('\n');

    // Test cases
    const tests = [
      {
        name: 'Fetch messages from #security',
        params: { channel: 'security' }
      },
      {
        name: 'Fetch limited messages from #general',
        params: { channel: 'general', limit: 5 }
      },
      {
        name: 'Try non-existent channel',
        params: { channel: 'nonexistent-channel-123' }
      }
    ];

    // Run tests
    for (const test of tests) {
      console.log(`\n=== ${test.name} ===`);
      try {
        const result = await runtime.handler(test.params, context);
        console.log('Result:', result);
      } catch (error) {
        console.error('Error:', error.message);
      }
      console.log('='.repeat(test.name.length + 8));
    }

  } catch (error) {
    console.error('\nTest failed:', error.message);
    if (error.response) {
      console.error('API Response:', error.response.data);
    }
    process.exit(1);
  }
}

// Run tests
testSlackReader().then(() => {
  console.log('\nTests completed.');
}).catch(error => {
  console.error('\nTest suite failed:', error);
  process.exit(1);
});