const logger = require('../utils/logger');
const axios = require('axios');
const { RateLimiterMemory } = require('rate-limiter-flexible');
const axiosRetry = require('axios-retry').default || require('axios-retry');

class VKApi {
  constructor() {
    this.baseURL = 'https://api.vk.com/method';
    this.token = process.env.VK_TOKEN;
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
    const ownerId = -groupId; // Negative for groups
    const params = {
      owner_id: ownerId,
      count: 10,
    };

    const response = await this._makeRequest('wall.get', params);

    const posts = response.items.map(post => ({
      id: post.id,
      text: post.text,
      date: post.date,
      likes: post.likes.count,
    }));

    return { posts };
  }

  async getComments(groupId, postId, offset = 0) {
    const ownerId = -groupId;
    let allComments = [];
    let currentOffset = offset;
    let hasMore = true;

    while (hasMore) {
      const params = {
        owner_id: ownerId,
        post_id: postId,
        offset: currentOffset,
        count: 100,
        extended: 1,
        fields: 'name', // Для from.name
      };

      const response = await this._makeRequest('wall.getComments', params);
      const items = response.items || [];

      allComments = allComments.concat(items.map(comment => ({
        id: comment.id,
        text: comment.text,
        from_id: comment.from_id,
        from: comment.from ? `${comment.from.first_name} ${comment.from.last_name}` : null,
        date: comment.date,
        likes: comment.likes ? comment.likes.count : 0,
      })));

      if (items.length < 100) {
        hasMore = false;
      } else {
        currentOffset += 100;
      }
    }

    return { comments: allComments, hasMore: false };
  }
}

const vkApiInstance = new VKApi();

module.exports = vkApiInstance;
module.exports.getPosts = vkApiInstance.getPosts.bind(vkApiInstance);
module.exports.getComments = vkApiInstance.getComments.bind(vkApiInstance);