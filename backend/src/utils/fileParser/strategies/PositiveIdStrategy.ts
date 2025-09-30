import { GroupParsingStrategy } from './GroupParsingStrategy';

/**
 * Стратегия парсинга положительного ID (например: 123)
 * Приоритет: 4
 */
export class PositiveIdStrategy implements GroupParsingStrategy {
  readonly name = 'positive_id';
  readonly priority = 4;
  readonly description = '<ID>';

  canParse(line: string): boolean {
    return /^\d+$/.test(line);
  }

  parse(line: string): { id: number | null; name: string | null } | null {
    if (/^\d+$/.test(line)) {
      const groupId = parseInt(line, 10);
      if (groupId > 0) {
        return { id: groupId, name: null };
      }
    }
    return null;
  }
}