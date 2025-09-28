import VKValidator from '../../src/utils/vkValidator';
import axios from 'axios';

// Мокаем axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('VKValidator Unit Tests', () => {
  let vkValidator: VKValidator;
  
  beforeEach(() => {
    vkValidator = new VKValidator({ accessToken: 'test-token' });
    // Сбрасываем мок перед каждым тестом
    jest.clearAllMocks();
  });
  
  describe('validateGroups', () => {
    it('should validate groups successfully', async () => {
      const groups = [
        { id: -123456789, name: 'Test Group 1' },
        { id: -987654321, name: 'Test Group 2' },
        { name: 'Group without ID' }
      ];
      
      // Мокаем успешный ответ VK API
      mockedAxios.get.mockResolvedValue({
        data: {
          response: [
            { id: 123456789, name: 'Test Group 1' },
            { id: 987654321, name: 'Test Group 2' }
          ]
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any
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
      mockedAxios.get.mockResolvedValue({
        data: {
          error: {
            error_msg: 'Rate limit exceeded'
          }
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any
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
  
  describe('checkApiHealth', () => {
    it('should return true for healthy API', async () => {
      mockedAxios.get.mockResolvedValue({
        data: {
          response: [{ id: 1 }]
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any
      });

      const result = await vkValidator.checkApiHealth();
      expect(result).toBe(true);
    });
    
    it('should return false for unhealthy API', async () => {
      mockedAxios.get.mockResolvedValue({
        data: {
          error: {
            error_msg: 'Invalid token'
          }
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any
      });

      const result = await vkValidator.checkApiHealth();
      expect(result).toBe(false);
    });
    
    it('should return false for network errors', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Network error'));

      const result = await vkValidator.checkApiHealth();
      expect(result).toBe(false);
    });
  });
});