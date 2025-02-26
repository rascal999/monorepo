const { runtime } = require('./handler');

// Mock Slack API responses
const mockChannelsResponse = {
  ok: true,
  channels: [
    {
      id: 'C1234567890',
      name: 'security',
      is_channel: true,
      is_archived: false
    },
    {
      id: 'C0987654321',
      name: 'general',
      is_channel: true,
      is_archived: false
    }
  ]
};

const mockMessagesResponse = {
  ok: true,
  messages: [
    {
      type: 'message',
      user: 'U1234567890',
      text: 'New security patch released for API gateway',
      ts: '1708794600.000000', // 2024-02-24 14:30:00
      reply_count: 2,
      reactions: [
        { name: '+1', count: 3 },
        { name: 'eyes', count: 2 }
      ]
    },
    {
      type: 'message',
      user: 'U0987654321',
      text: 'Deploying to staging for testing',
      ts: '1708794675.000000', // 2024-02-24 14:31:15
      reactions: [
        { name: 'rocket', count: 1 }
      ]
    }
  ]
};

const mockUsersResponse = {
  ok: true,
  members: [
    {
      id: 'U1234567890',
      name: 'johndoe',
      real_name: 'John Doe'
    },
    {
      id: 'U0987654321',
      name: 'janesmith',
      real_name: 'Jane Smith'
    }
  ]
};

// Mock WebClient class
class MockWebClient {
  constructor(token) {
    this.token = token;
    this.conversations = {
      list: jest.fn().mockResolvedValue(mockChannelsResponse),
      history: jest.fn().mockResolvedValue(mockMessagesResponse)
    };
    this.users = {
      list: jest.fn().mockResolvedValue(mockUsersResponse)
    };
  }
}

// Mock @slack/web-api module
jest.mock('@slack/web-api', () => ({
  WebClient: jest.fn().mockImplementation((token) => new MockWebClient(token))
}));

describe('Slack Channel Reader Agent', () => {
  let mockWebClient;
  const context = {
    introspect: jest.fn()
  };

  beforeEach(() => {
    runtime.runtimeArgs = {
      SLACK_TOKEN: 'xoxp-test-token'
    };
    context.introspect.mockClear();
    mockWebClient = new MockWebClient();
    jest.clearAllMocks();
  });

  test('fetches messages from a channel', async () => {
    const result = await runtime.handler({ channel: 'security' }, context);
    
    expect(result).toContain('Here are the last 2 messages from #security');
    expect(result).toContain('John Doe');
    expect(result).toContain('New security patch released for API gateway');
    expect(result).toContain('(2 replies in thread)');
    expect(result).toContain('Reactions: +1: 3, eyes: 2');
    expect(result).toContain('Jane Smith');
    expect(result).toContain('Deploying to staging for testing');
    expect(result).toContain('Reactions: rocket: 1');
  });

  test('handles non-existent channel', async () => {
    const { WebClient } = require('@slack/web-api');
    const mockClient = new WebClient();
    mockClient.conversations.list.mockResolvedValueOnce({
      ok: true,
      channels: []
    });

    const result = await runtime.handler({ channel: 'nonexistent' }, context);
    expect(result).toBe('Channel #nonexistent not found');
  });

  test('handles authentication error', async () => {
    const { WebClient } = require('@slack/web-api');
    const mockClient = new WebClient();
    mockClient.conversations.list.mockRejectedValueOnce({
      response: { status: 401 }
    });

    const result = await runtime.handler({ channel: 'security' }, context);
    expect(result).toBe('Authentication failed. Please check your Slack token.');
  });

  test('handles missing token', async () => {
    runtime.runtimeArgs = {};
    const result = await runtime.handler({ channel: 'security' }, context);
    expect(result).toBe('Missing required Slack token. Please configure it in the agent skills settings.');
  });

  test('handles missing channel parameter', async () => {
    const result = await runtime.handler({}, context);
    expect(result).toBe("Missing required field: channel (e.g., 'security')");
  });

  test('handles empty channel', async () => {
    const { WebClient } = require('@slack/web-api');
    const mockClient = new WebClient();
    mockClient.conversations.list.mockResolvedValueOnce({
      ok: true,
      channels: [{ id: 'C1234567890', name: 'empty' }]
    });
    mockClient.conversations.history.mockResolvedValueOnce({
      ok: true,
      messages: []
    });

    const result = await runtime.handler({ channel: 'empty' }, context);
    expect(result).toBe('No messages found in #empty');
  });
});