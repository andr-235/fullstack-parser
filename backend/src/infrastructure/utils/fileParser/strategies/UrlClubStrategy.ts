import { GroupParsingStrategy } from './GroupParsingStrategy';

/**
 * Стратегия парсинга URL формата https://vk.com/club<ID>
 * Приоритет: 1 (самый высокий) - точный формат
 */
export class UrlClubStrategy implements GroupParsingStrategy {
  readonly name = 'url_club';
  readonly priority = 1;
  readonly description = 'https://vk.com/club<ID>';

  canParse(line: string): boolean {
    return /^https:\/\/vk\.com\/club\d+$/i.test(line);
  }

  parse(line: string): { id: number | null; name: string | null } | null {
    const match = line.match(/^https:\/\/vk\.com\/club(\d+)$/i);
    if (match) {
      const id = parseInt(match[1], 10);
      return id > 0 ? { id, name: null } : null;
    }
    return null;
  }
}