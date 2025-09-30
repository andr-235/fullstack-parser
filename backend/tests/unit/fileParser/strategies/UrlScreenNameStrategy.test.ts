import { UrlScreenNameStrategy } from '@/utils/fileParser/strategies/UrlScreenNameStrategy';

describe('UrlScreenNameStrategy', () => {
  let strategy: UrlScreenNameStrategy;

  beforeEach(() => {
    strategy = new UrlScreenNameStrategy();
  });

  describe('properties', () => {
    it('should have correct name', () => {
      expect(strategy.name).toBe('url_screen_name');
    });

    it('should have priority 2', () => {
      expect(strategy.priority).toBe(2);
    });

    it('should have correct description', () => {
      expect(strategy.description).toBe('https://vk.com/<screen_name>');
    });
  });

  describe('canParse()', () => {
    it('should return true for valid screen_name URL', () => {
      expect(strategy.canParse('https://vk.com/durov')).toBe(true);
      expect(strategy.canParse('https://vk.com/testgroup')).toBe(true);
      expect(strategy.canParse('https://vk.com/test_group123')).toBe(true);
    });

    it('should return true for URL with underscores and numbers', () => {
      expect(strategy.canParse('https://vk.com/my_group_2024')).toBe(true);
    });

    it('should return false for club URL', () => {
      expect(strategy.canParse('https://vk.com/club123')).toBe(false);
      expect(strategy.canParse('https://vk.com/club456')).toBe(false);
    });

    it('should return false for invalid formats', () => {
      expect(strategy.canParse('durov')).toBe(false);
      expect(strategy.canParse('123')).toBe(false);
      expect(strategy.canParse('-123')).toBe(false);
    });

    it('should return false for URL with special characters', () => {
      expect(strategy.canParse('https://vk.com/test-group')).toBe(false);
      expect(strategy.canParse('https://vk.com/test.group')).toBe(false);
    });
  });

  describe('parse()', () => {
    it('should extract screen_name from valid URL', () => {
      const result = strategy.parse('https://vk.com/durov');
      expect(result).toEqual({ id: null, name: 'durov' });
    });

    it('should extract screen_name with underscores', () => {
      const result = strategy.parse('https://vk.com/my_group_123');
      expect(result).toEqual({ id: null, name: 'my_group_123' });
    });

    it('should handle uppercase URL', () => {
      const result = strategy.parse('HTTPS://VK.COM/TestGroup');
      expect(result).toEqual({ id: null, name: 'TestGroup' });
    });

    it('should return null for "club" without ID', () => {
      const result = strategy.parse('https://vk.com/club');
      expect(result).toBeNull();
    });

    it('should return screen_name for club URL with ID if called directly', () => {
      // canParse вернет false для club123, но parse все равно обработает
      const result = strategy.parse('https://vk.com/club123');
      expect(result).toEqual({ id: null, name: 'club123' });
    });

    it('should return null for invalid format', () => {
      expect(strategy.parse('durov')).toBeNull();
      expect(strategy.parse('123')).toBeNull();
    });
  });
});