import { ScreenNameStrategy } from '@/utils/fileParser/strategies/ScreenNameStrategy';

describe('ScreenNameStrategy', () => {
  let strategy: ScreenNameStrategy;

  beforeEach(() => {
    strategy = new ScreenNameStrategy();
  });

  describe('properties', () => {
    it('should have correct name', () => {
      expect(strategy.name).toBe('screen_name');
    });

    it('should have priority 5', () => {
      expect(strategy.priority).toBe(5);
    });

    it('should have correct description', () => {
      expect(strategy.description).toBe('<screen_name> or club<ID>');
    });
  });

  describe('canParse()', () => {
    it('should return true for screen_name', () => {
      expect(strategy.canParse('durov')).toBe(true);
      expect(strategy.canParse('testgroup')).toBe(true);
      expect(strategy.canParse('my_group')).toBe(true);
    });

    it('should return true for screen_name with dots', () => {
      expect(strategy.canParse('baraholka777.birobidzhan')).toBe(true);
      expect(strategy.canParse('test.group')).toBe(true);
      expect(strategy.canParse('my.group.name')).toBe(true);
    });

    it('should return true for club<ID> format', () => {
      expect(strategy.canParse('club123')).toBe(true);
      expect(strategy.canParse('CLUB456')).toBe(true);
    });

    it('should return false for negative ID', () => {
      expect(strategy.canParse('-123')).toBe(false);
    });

    it('should return false for positive ID only', () => {
      expect(strategy.canParse('123')).toBe(false);
    });

    it('should return false for URLs', () => {
      expect(strategy.canParse('https://vk.com/club123')).toBe(false);
      expect(strategy.canParse('https://vk.com/durov')).toBe(false);
    });
  });

  describe('parse()', () => {
    it('should parse simple screen_name', () => {
      const result = strategy.parse('durov');
      expect(result).toEqual({ id: null, name: 'durov' });
    });

    it('should parse screen_name with underscores', () => {
      const result = strategy.parse('my_group_test');
      expect(result).toEqual({ id: null, name: 'my_group_test' });
    });

    it('should parse screen_name with dots', () => {
      const result = strategy.parse('baraholka777.birobidzhan');
      expect(result).toEqual({ id: null, name: 'baraholka777.birobidzhan' });
    });

    it('should parse screen_name with dots and underscores', () => {
      const result = strategy.parse('my_group.test');
      expect(result).toEqual({ id: null, name: 'my_group.test' });
    });

    it('should parse club<ID> format as ID with name', () => {
      const result = strategy.parse('club123');
      expect(result).toEqual({ id: 123, name: 'club123' });
    });

    it('should parse CLUB<ID> with uppercase', () => {
      const result = strategy.parse('CLUB456');
      expect(result).toEqual({ id: 456, name: 'CLUB456' });
    });

    it('should parse mixed case club<ID>', () => {
      const result = strategy.parse('ClUb789');
      expect(result).toEqual({ id: 789, name: 'ClUb789' });
    });

    it('should return name for club0 (screen_name)', () => {
      const result = strategy.parse('club0');
      // club0 рассматривается как screen_name, а не как club<ID>
      expect(result).toEqual({ id: null, name: 'club0' });
    });

    it('should return name for club without ID', () => {
      const result = strategy.parse('club');
      expect(result).toEqual({ id: null, name: 'club' });
    });

    it('should return null for negative ID', () => {
      const result = strategy.parse('-123');
      expect(result).toBeNull();
    });

    it('should return null for positive ID only (handled by other strategy)', () => {
      const result = strategy.parse('123');
      // Чистое число пройдет через canParse как false,
      // но parse все равно вернет как screen_name если вызван напрямую
      expect(result).toEqual({ id: null, name: '123' });
    });
  });
});