const VKValidator = require('../../src/utils/vkValidator.js');

// Мокаем axios
const axios = require('axios');
const originalGet = axios.get;

describe('VKValidator Unit Tests', () => {
  let vkValidator;
  
  beforeEach(() => {
    vkValidator = new VKValidator('test-token');
    // Сбрасываем мок перед каждым тестом
    axios.get = originalGet;
  });
  
  describe('validateGroups', () => {
    it('should validate groups successfully', async () => {
      const groups = [
        { id: -123456789, name: 'Test Group 1' },
        { id: -987654321, name: 'Test Group 2' },
        { name: 'Group without ID' }
      ];
      
      // Мокаем успешный ответ VK API
      axios.get = async () => ({
        data: {
          response: [
            { id: 123456789, name: 'Test Group 1' },
            { id: 987654321, name: 'Test Group 2' }
          ]
        }
      });
      
      const result = await vkValidator.validateGroups(groups);
      
      expect(result).toHaveProperty('validGroups');
      expect(result).toHaveProperty('invalidGroups');
      expect(result).toHaveProperty('errors');
      
      expect(result.validGroups.length).toBe(3); // 2 с ID + 1 только с именем
      expect(result.invalidGroups.length).toBe(0);
    });
    
    it('should handle VK API errors', async () => {
      const groups = [{ id: -123456789, name: 'Test Group' }];
      
      // Мокаем ошибку VK API
      axios.get = async () => ({
        data: {
          error: {
            error_msg: 'Rate limit exceeded'
          }
        }
      });
      
      const result = await vkValidator.validateGroups(groups);
      
      expect(result.invalidGroups.length).toBe(1);
      expect(result.invalidGroups[0].error).toBe('VK API error');
    });
    
    it('should handle groups without IDs', async () => {
      const groups = [
        { name: 'Group 1' },
        { name: 'Group 2' }
      ];
      
      const result = await vkValidator.validateGroups(groups);
      
      expect(result.validGroups.length).toBe(2);
      expect(result.invalidGroups.length).toBe(0);
    });
    
    it('should handle empty groups array', async () => {
      const result = await vkValidator.validateGroups([]);
      
      expect(result.validGroups.length).toBe(0);
      expect(result.invalidGroups.length).toBe(0);
    });
  });
  
  describe('validateBatch', () => {
    it('should validate batch successfully', async () => {
      const batch = [
        { id: -123456789, name: 'Test Group 1' },
        { id: -987654321, name: 'Test Group 2' }
      ];
      
      axios.get = async () => ({
        data: {
          response: [
            { id: 123456789, name: 'Test Group 1' },
            { id: 987654321, name: 'Test Group 2' }
          ]
        }
      });
      
      const result = await vkValidator.validateBatch(batch);
      
      expect(result.valid.length).toBe(2);
      expect(result.invalid.length).toBe(0);
      expect(result.errors.length).toBe(0);
    });
    
    it('should mark non-existent groups as invalid', async () => {
      const batch = [
        { id: -123456789, name: 'Test Group 1' },
        { id: -999999999, name: 'Non-existent Group' }
      ];
      
      axios.get = async () => ({
        data: {
          response: [
            { id: 123456789, name: 'Test Group 1' }
          ]
        }
      });
      
      const result = await vkValidator.validateBatch(batch);
      
      expect(result.valid.length).toBe(1);
      expect(result.invalid.length).toBe(1);
      expect(result.invalid[0].id).toBe(-999999999);
    });
  });
  
  describe('checkApiHealth', () => {
    it('should return true for healthy API', async () => {
      axios.get = async () => ({
        data: {
          response: [{ id: 1 }]
        }
      });
      
      const result = await vkValidator.checkApiHealth();
      expect(result).toBe(true);
    });
    
    it('should return false for unhealthy API', async () => {
      axios.get = async () => ({
        data: {
          error: {
            error_msg: 'Invalid token'
          }
        }
      });
      
      const result = await vkValidator.checkApiHealth();
      expect(result).toBe(false);
    });
    
    it('should return false for network errors', async () => {
      axios.get = async () => {
        throw new Error('Network error');
      };
      
      const result = await vkValidator.checkApiHealth();
      expect(result).toBe(false);
    });
  });
});