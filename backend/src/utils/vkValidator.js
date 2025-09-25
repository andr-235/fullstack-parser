const axios = require('axios');
const logger = require('./logger.js');

class VKValidator {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.baseURL = 'https://api.vk.com/method';
    this.rateLimit = 3; // запросов в секунду
    this.lastRequestTime = 0;
  }
  
  /**
   * Валидирует группы через VK API
   * @param {Array} groups - Массив групп для валидации
   * @returns {Object} Результат валидации
   */
  async validateGroups(groups) {
    const validGroups = [];
    const invalidGroups = [];
    const errors = [];
    
    // Фильтруем только группы с ID (отрицательные числа)
    const groupsWithId = groups.filter(group => group.id && group.id < 0);
    
    if (groupsWithId.length === 0) {
      return {
        validGroups: groups.filter(group => !group.id), // Группы только с именами
        invalidGroups: [],
        errors: []
      };
    }
    
    // Обрабатываем группы батчами по 10
    const batchSize = 10;
    for (let i = 0; i < groupsWithId.length; i += batchSize) {
      const batch = groupsWithId.slice(i, i + batchSize);
      
      try {
        await this.rateLimitDelay();
        const batchResult = await this.validateBatch(batch);
        
        validGroups.push(...batchResult.valid);
        invalidGroups.push(...batchResult.invalid);
        errors.push(...batchResult.errors);
        
        logger.info('Batch validated', {
          batch: Math.floor(i / batchSize) + 1,
          total: Math.ceil(groupsWithId.length / batchSize),
          valid: batchResult.valid.length,
          invalid: batchResult.invalid.length
        });
      } catch (error) {
        logger.error('Batch validation failed', { 
          batch: Math.floor(i / batchSize) + 1, 
          error: error.message 
        });
        
        // Помечаем все группы в батче как невалидные
        batch.forEach(group => {
          invalidGroups.push({
            ...group,
            error: 'VK API error'
          });
        });
        
        errors.push({
          batch: Math.floor(i / batchSize) + 1,
          error: error.message,
          groups: batch.map(g => g.id)
        });
      }
    }
    
    // Добавляем группы только с именами как валидные
    const nameOnlyGroups = groups.filter(group => !group.id);
    validGroups.push(...nameOnlyGroups);
    
    return {
      validGroups,
      invalidGroups,
      errors
    };
  }
  
  /**
   * Валидирует батч групп через VK API
   * @param {Array} batch - Батч групп
   * @returns {Object} Результат валидации батча
   */
  async validateBatch(batch) {
    const groupIds = batch.map(group => group.id).join(',');
    
    const response = await axios.get(`${this.baseURL}/groups.getById`, {
      params: {
        group_ids: groupIds,
        access_token: this.accessToken,
        v: '5.131'
      },
      timeout: 10000
    });
    
    if (response.data.error) {
      throw new Error(`VK API error: ${response.data.error.error_msg}`);
    }
    
    const validGroups = [];
    const invalidGroups = [];
    const errors = [];
    
    const validGroupIds = new Set(
      response.data.response.map(group => -group.id)
    );
    
    batch.forEach(group => {
      if (validGroupIds.has(group.id)) {
        const vkGroup = response.data.response.find(g => -g.id === group.id);
        validGroups.push({
          ...group,
          name: vkGroup.name || group.name,
          status: 'valid'
        });
      } else {
        invalidGroups.push({
          ...group,
          status: 'invalid',
          error: 'Group not found'
        });
      }
    });
    
    return {
      valid: validGroups,
      invalid: invalidGroups,
      errors
    };
  }
  
  /**
   * Задержка для соблюдения rate limit
   */
  async rateLimitDelay() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    const minInterval = 1000 / this.rateLimit; // 333ms между запросами
    
    if (timeSinceLastRequest < minInterval) {
      const delay = minInterval - timeSinceLastRequest;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    this.lastRequestTime = Date.now();
  }
  
  /**
   * Проверяет доступность VK API
   * @returns {boolean} Доступность API
   */
  async checkApiHealth() {
    try {
      await this.rateLimitDelay();
      const response = await axios.get(`${this.baseURL}/users.get`, {
        params: {
          access_token: this.accessToken,
          v: '5.131'
        },
        timeout: 5000
      });
      
      return !response.data.error;
    } catch (error) {
      logger.error('VK API health check failed', { error: error.message });
      return false;
    }
  }
}

module.exports = VKValidator;
