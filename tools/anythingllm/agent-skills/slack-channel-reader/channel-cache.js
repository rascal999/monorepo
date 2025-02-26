const fs = require('fs');
const path = require('path');

class ChannelCache {
  constructor() {
    this.cacheFile = path.join(__dirname, '.channel-cache.json');
  }

  async load() {
    try {
      if (fs.existsSync(this.cacheFile)) {
        const data = fs.readFileSync(this.cacheFile, 'utf8');
        return JSON.parse(data);
      }
    } catch (error) {
      console.error('Error loading channel cache:', error);
    }
    return {};
  }

  async save(channels) {
    try {
      const cache = {};
      channels.forEach(channel => {
        cache[channel.name] = {
          id: channel.id,
          name: channel.name,
          is_private: channel.is_private,
          updated_at: new Date().toISOString()
        };
      });
      fs.writeFileSync(this.cacheFile, JSON.stringify(cache, null, 2));
      return cache;
    } catch (error) {
      console.error('Error saving channel cache:', error);
      throw error;
    }
  }

  async getChannelId(channelName) {
    const cache = await this.load();
    return cache[channelName]?.id;
  }

  async getChannel(channelName) {
    const cache = await this.load();
    return cache[channelName];
  }

  async getAllChannels() {
    const cache = await this.load();
    return Object.values(cache);
  }

  async isStale() {
    try {
      if (!fs.existsSync(this.cacheFile)) {
        return true;
      }
      const stats = fs.statSync(this.cacheFile);
      const ageInDays = (Date.now() - stats.mtimeMs) / (1000 * 60 * 60 * 24);
      // Cache is stale if older than 30 days
      return ageInDays > 30;
    } catch (error) {
      console.error('Error checking cache staleness:', error);
      return true;
    }
  }
}

module.exports = new ChannelCache();