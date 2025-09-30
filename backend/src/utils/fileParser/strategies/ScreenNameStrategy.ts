import { GroupParsingStrategy } from './GroupParsingStrategy';

/**
 * Стратегия парсинга screen_name (например: durov, club123)
 * Если формат club<ID> - парсит как ID с сохранением имени
 * Приоритет: 5 (самый низкий) - fallback стратегия
 */
export class ScreenNameStrategy implements GroupParsingStrategy {
  readonly name = 'screen_name';
  readonly priority = 5;
  readonly description = '<screen_name> or club<ID>';

  canParse(line: string): boolean {
    // Не должно быть отрицательным ID или чистым числом
    if (line.startsWith('-') || /^\d+$/.test(line)) {
      return false;
    }

    // Валидный screen_name: буквы, цифры, подчеркивание
    return /^[a-zA-Z0-9_]+$/.test(line);
  }

  parse(line: string): { id: number | null; name: string | null } | null {
    // Проверяем формат club<ID>
    const match = line.match(/^club(\d+)$/i);
    if (match) {
      const groupId = parseInt(match[1], 10);
      if (groupId > 0) {
        return { id: groupId, name: line };
      }
    }

    // Просто screen_name - дополнительная проверка формата
    if (/^[a-zA-Z0-9_]+$/.test(line)) {
      return { id: null, name: line };
    }

    return null;
  }
}