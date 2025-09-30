import { UrlClubStrategy } from '@/utils/fileParser/strategies/UrlClubStrategy';

describe('UrlClubStrategy', () => {
  let strategy: UrlClubStrategy;

  beforeEach(() => {
    strategy = new UrlClubStrategy();
  });

  describe('properties', () => {
    it('should have correct name', () => {
      expect(strategy.name).toBe('url_club');
    });

    it('should have priority 1', () => {
      expect(strategy.priority).toBe(1);
    });

    it('should have correct description', () => {
      expect(strategy.description).toBe('https://vk.com/club<ID>');
    });
  });

  describe('canParse()', () => {
    it('should return true for valid club URL', () => {
      expect(strategy.canParse('https://vk.com/club123')).toBe(true);
      expect(strategy.canParse('https://vk.com/club456789')).toBe(true);
    });

    it('should return true for club URL with different case', () => {
      expect(strategy.canParse('https://VK.COM/CLUB123')).toBe(true);
      expect(strategy.canParse('HTTPS://vk.com/club123')).toBe(true);
    });

    it('should return false for screen_name URL', () => {
      expect(strategy.canParse('https://vk.com/durov')).toBe(false);
      expect(strategy.canParse('https://vk.com/testgroup')).toBe(false);
    });

    it('should return false for invalid formats', () => {
      expect(strategy.canParse('123')).toBe(false);
      expect(strategy.canParse('club123')).toBe(false);
      expect(strategy.canParse('-123')).toBe(false);
      expect(strategy.canParse('https://vk.com/club')).toBe(false);
    });

    it('should return false for URL with path after club ID', () => {
      expect(strategy.canParse('https://vk.com/club123/wall')).toBe(false);
    });

    it('should accept club0 in canParse but parse will reject', () => {
      // canParse принимает формат, а parse проверяет > 0
      expect(strategy.canParse('https://vk.com/club0')).toBe(true);
    });
  });

  describe('parse()', () => {
    it('should extract group ID from valid club URL', () => {
      const result = strategy.parse('https://vk.com/club123');
      expect(result).toEqual({ id: 123, name: null });
    });

    it('should extract large group ID', () => {
      const result = strategy.parse('https://vk.com/club987654321');
      expect(result).toEqual({ id: 987654321, name: null });
    });

    it('should handle uppercase URL', () => {
      const result = strategy.parse('HTTPS://VK.COM/CLUB456');
      expect(result).toEqual({ id: 456, name: null });
    });

    it('should return null for club0', () => {
      const result = strategy.parse('https://vk.com/club0');
      expect(result).toBeNull();
    });

    it('should return null for negative club ID', () => {
      const result = strategy.parse('https://vk.com/club-123');
      expect(result).toBeNull();
    });

    it('should return null for invalid format', () => {
      expect(strategy.parse('https://vk.com/durov')).toBeNull();
      expect(strategy.parse('club123')).toBeNull();
      expect(strategy.parse('123')).toBeNull();
    });
  });
});