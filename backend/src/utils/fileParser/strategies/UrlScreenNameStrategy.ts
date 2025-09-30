import { GroupParsingStrategy } from './GroupParsingStrategy';

/**
 * Стратегия парсинга URL формата https://vk.com/<screen_name>
 * Приоритет: 2 - исключая club<ID>
 */
export class UrlScreenNameStrategy implements GroupParsingStrategy {
  readonly name = 'url_screen_name';
  readonly priority = 2;
  readonly description = 'https://vk.com/<screen_name>';

  canParse(line: string): boolean {
    // Проверяем что это URL, но не club<ID>
    return /^https:\/\/vk\.com\/[a-zA-Z0-9_]+$/i.test(line) &&
           !line.match(/^https:\/\/vk\.com\/club\d+$/i);
  }

  parse(line: string): { id: number | null; name: string | null } | null {
    const match = line.match(/^https:\/\/vk\.com\/([a-zA-Z0-9_]+)$/i);
    if (match) {
      const screenName = match[1];
      // Исключаем просто 'club' без ID
      if (screenName.toLowerCase() !== 'club') {
        return { id: null, name: screenName };
      }
    }
    return null;
  }
}