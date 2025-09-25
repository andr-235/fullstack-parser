const logger = require('../utils/logger.js');

const axios = require('axios');
const { RateLimiterMemory } = require('rate-limiter-flexible');
const axiosRetry = require('axios-retry');

class VKApi {
  constructor() {
    this.baseURL = 'https://api.vk.com/method';
    this.token = process.env.VK_ACCESS_TOKEN;
    this.version = '5.199';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
    });

    this.rateLimiter = new RateLimiterMemory({
      points: 3,
      duration: 1,
    });

    // Interceptor для rate limiting
    this.client.interceptors.request.use(async (config) => {
      await this.rateLimiter.consume('vk-api');
      return config;
    });

    // Retry config с exponential backoff
    axiosRetry(this.client, {
      retries: 3,
      retryDelay: axiosRetry.exponentialDelay,
      retryCondition: (error) => {
        return error.code === 'ECONNABORTED' || error.response?.status >= 500;
      },
    });
  }

  async _makeRequest(method, params) {
    try {
      const response = await this.client.get(method, {
        params: {
          ...params,
          access_token: this.token,
          v: this.version,
        },
      });

      const data = response.data;
      if (data.error) {
        const error = new Error(`VK API error: ${data.error.error_msg} (code: ${data.error.error_code})`);
        logger.error('VK API error', { error: data.error, method });
        throw error;
      }

      return data.response;
    } catch (error) {
      if (error.response) {
        logger.error('HTTP Error', { status: error.response.status, message: error.message, method });
      } else if (error.request) {
        logger.error('Request Error', { message: error.message, method });
      } else {
        logger.error('Error', { message: error.message, method });
      }
      throw error;
    }
  }

  async getPosts(groupId) {
    const ownerId = -Math.abs(groupId); // Ensure negative for groups
    const params = {
      owner_id: ownerId,
      count: 10,
    };

    const response = await this._makeRequest('wall.get', params);

    const posts = response.items.map(post => ({
      vk_post_id: post.id,
      owner_id: ownerId,
      group_id: Math.abs(groupId),
      text: post.text || '',
      date: new Date(post.date * 1000),
      likes: post.likes?.count || 0,
    }));

    return { posts };
  }

  async getComments(groupId, postVkId, offset = 0) {
    const ownerId = -Math.abs(groupId); // Ensure negative for groups
    let allComments = [];
    let currentOffset = offset;
    let hasMore = true;
    let maxIterations = 100; // Максимум 10,000 комментариев (100 * 100)

    while (hasMore && maxIterations > 0) {
      maxIterations--;
      const params = {
        owner_id: ownerId,
        post_id: postVkId,
        offset: currentOffset,
        count: 100,
        extended: 1,
        fields: 'first_name,last_name',
      };

      const response = await this._makeRequest('wall.getComments', params);
      const items = response.items || [];
      const profiles = response.profiles || [];

      // Create profile mapping for author names
      const profileMap = profiles.reduce((map, profile) => {
        map[profile.id] = `${profile.first_name} ${profile.last_name}`;
        return map;
      }, {});

      allComments = allComments.concat(items.map(comment => ({
        vk_comment_id: comment.id,
        post_vk_id: postVkId,
        owner_id: ownerId,
        author_id: comment.from_id,
        author_name: profileMap[comment.from_id] || `User ${comment.from_id}`,
        text: comment.text || '',
        date: new Date(comment.date * 1000),
        likes: comment.likes?.count || 0,
      })));

      if (items.length < 100) {
        hasMore = false;
      } else {
        currentOffset += 100;
      }
    }

    if (maxIterations <= 0) {
      logger.warn('Comments pagination reached maximum limit', {
        groupId,
        postVkId,
        currentOffset,
        commentsCount: allComments.length
      });
    }

    return { comments: allComments, hasMore: false };
  }
}

module.exports = new VKApi();