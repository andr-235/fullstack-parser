import { GroupLineParser } from '@/utils/fileParser/GroupLineParser';
import { ValidationError } from '@/utils/errors';
import {
  UrlClubStrategy,
  UrlScreenNameStrategy,
  NegativeIdStrategy,
  PositiveIdStrategy,
  ScreenNameStrategy,
  GroupParsingStrategy
} from '@/utils/fileParser/strategies';

describe('GroupLineParser', () => {
  let parser: GroupLineParser;

  beforeEach(() => {
    parser = new GroupLineParser();
  });

  describe('constructor', () => {
    it('should initialize with default strategies', () => {
      const strategies = parser.getStrategies();
      expect(strategies).toHaveLength(5);
      expect(strategies[0]).toBeInstanceOf(UrlClubStrategy);
      expect(strategies[1]).toBeInstanceOf(UrlScreenNameStrategy);
      expect(strategies[2]).toBeInstanceOf(NegativeIdStrategy);
      expect(strategies[3]).toBeInstanceOf(PositiveIdStrategy);
      expect(strategies[4]).toBeInstanceOf(ScreenNameStrategy);
    });

    it('should sort strategies by priority', () => {
      const strategies = parser.getStrategies();
      for (let i = 0; i < strategies.length - 1; i++) {
        expect(strategies[i].priority).toBeLessThanOrEqual(strategies[i + 1].priority);
      }
    });
  });

  describe('parse()', () => {
    describe('URL club format', () => {
      it('should parse https://vk.com/club123', () => {
        const result = parser.parse('https://vk.com/club123', 1);
        expect(result).toEqual({ id: 123, name: null, strategyName: 'url_club' });
      });

      it('should parse uppercase URL', () => {
        const result = parser.parse('HTTPS://VK.COM/CLUB456', 1);
        expect(result).toEqual({ id: 456, name: null, strategyName: 'url_club' });
      });
    });

    describe('URL screen_name format', () => {
      it('should parse https://vk.com/durov', () => {
        const result = parser.parse('https://vk.com/durov', 1);
        expect(result).toEqual({ id: null, name: 'durov', strategyName: 'url_screen_name' });
      });
    });

    describe('Negative ID format', () => {
      it('should parse -123 as positive ID', () => {
        const result = parser.parse('-123', 1);
        expect(result).toEqual({ id: 123, name: null, strategyName: 'negative_id' });
      });
    });

    describe('Positive ID format', () => {
      it('should parse 123', () => {
        const result = parser.parse('123', 1);
        expect(result).toEqual({ id: 123, name: null, strategyName: 'positive_id' });
      });
    });

    describe('Screen name format', () => {
      it('should parse durov', () => {
        const result = parser.parse('durov', 1);
        expect(result).toEqual({ id: null, name: 'durov', strategyName: 'screen_name' });
      });

      it('should parse club123 format', () => {
        const result = parser.parse('club123', 1);
        expect(result).toEqual({ id: 123, name: 'club123', strategyName: 'screen_name' });
      });
    });

    describe('Invalid formats', () => {
      it('should throw ValidationError for invalid format', () => {
        expect(() => {
          parser.parse('invalid@#$%', 5);
        }).toThrow(ValidationError);
      });

      it('should include line number in error', () => {
        try {
          parser.parse('invalid@#$%', 42);
          fail('Should have thrown ValidationError');
        } catch (error) {
          expect(error).toBeInstanceOf(ValidationError);
          const validationError = error as ValidationError;
          expect(validationError.details[0].field).toBe('line_42');
        }
      });

      it('should include line content in error', () => {
        try {
          parser.parse('invalid@#$%', 1);
          fail('Should have thrown ValidationError');
        } catch (error) {
          expect(error).toBeInstanceOf(ValidationError);
          const validationError = error as ValidationError;
          expect(validationError.details[0].value).toBe('invalid@#$%');
        }
      });
    });
  });

  describe('addStrategy()', () => {
    it('should add new strategy', () => {
      const customStrategy: GroupParsingStrategy = {
        name: 'custom',
        priority: 0,
        description: 'Custom format',
        canParse: (line) => line.startsWith('@'),
        parse: (line) => ({ id: null, name: line.slice(1) })
      };

      parser.addStrategy(customStrategy);
      const strategies = parser.getStrategies();
      expect(strategies).toHaveLength(6);
      expect(strategies[0]).toBe(customStrategy);
    });

    it('should maintain priority order after adding', () => {
      const customStrategy: GroupParsingStrategy = {
        name: 'custom',
        priority: 2.5,
        description: 'Custom format',
        canParse: () => false,
        parse: () => null
      };

      parser.addStrategy(customStrategy);
      const strategies = parser.getStrategies();

      for (let i = 0; i < strategies.length - 1; i++) {
        expect(strategies[i].priority).toBeLessThanOrEqual(strategies[i + 1].priority);
      }
    });
  });

  describe('removeStrategy()', () => {
    it('should remove strategy by name', () => {
      const removed = parser.removeStrategy('url_club');
      expect(removed).toBe(true);

      const strategies = parser.getStrategies();
      expect(strategies).toHaveLength(4);
      expect(strategies.find(s => s.name === 'url_club')).toBeUndefined();
    });

    it('should return false for non-existent strategy', () => {
      const removed = parser.removeStrategy('non_existent');
      expect(removed).toBe(false);
    });

    it('should maintain parsing after removal', () => {
      parser.removeStrategy('url_club');

      // URL club format should fail now
      expect(() => {
        parser.parse('https://vk.com/club123', 1);
      }).toThrow(ValidationError);

      // But other formats should work
      const result = parser.parse('123', 1);
      expect(result.id).toBe(123);
    });
  });

  describe('getStrategies()', () => {
    it('should return readonly copy of strategies', () => {
      const strategies = parser.getStrategies();
      expect(Array.isArray(strategies)).toBe(true);
      expect(strategies.length).toBeGreaterThan(0);
    });

    it('should return copy that does not affect internal state', () => {
      const strategies = parser.getStrategies();
      const originalLength = strategies.length;

      // Модификация возвращенного массива не должна влиять на внутренний
      (strategies as any).push({});

      // Убедимся что внутренний массив не изменился
      expect(parser.getStrategies()).toHaveLength(originalLength);
    });
  });
});