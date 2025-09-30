import { GroupParsingStrategy } from './GroupParsingStrategy';

/**
 * Стратегия парсинга отрицательного ID (например: -123)
 * Возвращает абсолютное значение ID
 * Приоритет: 3
 */
export class NegativeIdStrategy implements GroupParsingStrategy {
  readonly name = 'negative_id';
  readonly priority = 3;
  readonly description = '-<ID>';

  canParse(line: string): boolean {
    return /^-\d+$/.test(line);
  }

  parse(line: string): { id: number | null; name: string | null } | null {
    if (line.startsWith('-') && /^-\d+$/.test(line)) {
      const groupId = parseInt(line, 10);
      if (groupId < 0) {
        return { id: Math.abs(groupId), name: null };
      }
    }
    return null;
  }
}