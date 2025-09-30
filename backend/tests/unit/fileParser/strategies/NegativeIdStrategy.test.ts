import { NegativeIdStrategy } from '@/utils/fileParser/strategies/NegativeIdStrategy';

describe('NegativeIdStrategy', () => {
  let strategy: NegativeIdStrategy;

  beforeEach(() => {
    strategy = new NegativeIdStrategy();
  });

  describe('properties', () => {
    it('should have correct name', () => {
      expect(strategy.name).toBe('negative_id');
    });

    it('should have priority 3', () => {
      expect(strategy.priority).toBe(3);
    });

    it('should have correct description', () => {
      expect(strategy.description).toBe('-<ID>');
    });
  });

  describe('canParse()', () => {
    it('should return true for negative ID', () => {
      expect(strategy.canParse('-123')).toBe(true);
      expect(strategy.canParse('-456789')).toBe(true);
      expect(strategy.canParse('-1')).toBe(true);
    });

    it('should return false for positive ID', () => {
      expect(strategy.canParse('123')).toBe(false);
    });

    it('should accept -0 in canParse but parse will reject', () => {
      expect(strategy.canParse('0')).toBe(false);
      // -0 проходит regex, но parse отклонит
      expect(strategy.canParse('-0')).toBe(true);
    });

    it('should return false for URLs', () => {
      expect(strategy.canParse('https://vk.com/club123')).toBe(false);
      expect(strategy.canParse('https://vk.com/durov')).toBe(false);
    });

    it('should return false for screen_name', () => {
      expect(strategy.canParse('durov')).toBe(false);
      expect(strategy.canParse('club123')).toBe(false);
    });

    it('should return false for negative with non-digits', () => {
      expect(strategy.canParse('-123abc')).toBe(false);
      expect(strategy.canParse('-12.34')).toBe(false);
    });
  });

  describe('parse()', () => {
    it('should convert negative ID to positive', () => {
      const result = strategy.parse('-123');
      expect(result).toEqual({ id: 123, name: null });
    });

    it('should handle large negative ID', () => {
      const result = strategy.parse('-987654321');
      expect(result).toEqual({ id: 987654321, name: null });
    });

    it('should handle -1', () => {
      const result = strategy.parse('-1');
      expect(result).toEqual({ id: 1, name: null });
    });

    it('should return null for -0', () => {
      const result = strategy.parse('-0');
      expect(result).toBeNull();
    });

    it('should return null for positive ID', () => {
      const result = strategy.parse('123');
      expect(result).toBeNull();
    });

    it('should return null for invalid format', () => {
      expect(strategy.parse('durov')).toBeNull();
      expect(strategy.parse('https://vk.com/club123')).toBeNull();
    });
  });
});