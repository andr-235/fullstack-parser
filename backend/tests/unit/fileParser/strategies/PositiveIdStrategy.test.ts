import { PositiveIdStrategy } from '@/utils/fileParser/strategies/PositiveIdStrategy';

describe('PositiveIdStrategy', () => {
  let strategy: PositiveIdStrategy;

  beforeEach(() => {
    strategy = new PositiveIdStrategy();
  });

  describe('properties', () => {
    it('should have correct name', () => {
      expect(strategy.name).toBe('positive_id');
    });

    it('should have priority 4', () => {
      expect(strategy.priority).toBe(4);
    });

    it('should have correct description', () => {
      expect(strategy.description).toBe('<ID>');
    });
  });

  describe('canParse()', () => {
    it('should return true for positive ID', () => {
      expect(strategy.canParse('123')).toBe(true);
      expect(strategy.canParse('456789')).toBe(true);
      expect(strategy.canParse('1')).toBe(true);
    });

    it('should return false for negative ID', () => {
      expect(strategy.canParse('-123')).toBe(false);
    });

    it('should accept zero in canParse but parse will reject', () => {
      // canParse принимает число, а parse проверяет > 0
      expect(strategy.canParse('0')).toBe(true);
    });

    it('should return false for URLs', () => {
      expect(strategy.canParse('https://vk.com/club123')).toBe(false);
      expect(strategy.canParse('https://vk.com/durov')).toBe(false);
    });

    it('should return false for screen_name', () => {
      expect(strategy.canParse('durov')).toBe(false);
      expect(strategy.canParse('club123')).toBe(false);
    });

    it('should return false for ID with non-digits', () => {
      expect(strategy.canParse('123abc')).toBe(false);
      expect(strategy.canParse('12.34')).toBe(false);
    });
  });

  describe('parse()', () => {
    it('should parse positive ID', () => {
      const result = strategy.parse('123');
      expect(result).toEqual({ id: 123, name: null });
    });

    it('should handle large positive ID', () => {
      const result = strategy.parse('987654321');
      expect(result).toEqual({ id: 987654321, name: null });
    });

    it('should handle ID 1', () => {
      const result = strategy.parse('1');
      expect(result).toEqual({ id: 1, name: null });
    });

    it('should return null for 0', () => {
      const result = strategy.parse('0');
      expect(result).toBeNull();
    });

    it('should return null for negative ID', () => {
      const result = strategy.parse('-123');
      expect(result).toBeNull();
    });

    it('should return null for invalid format', () => {
      expect(strategy.parse('durov')).toBeNull();
      expect(strategy.parse('https://vk.com/club123')).toBeNull();
    });
  });
});