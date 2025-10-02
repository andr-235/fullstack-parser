/**
 * Интерфейс стратегии парсинга VK групп.
 * Реализует паттерн Strategy для гибкого расширения форматов парсинга.
 */
export interface GroupParsingStrategy {
  /** Уникальное имя стратегии */
  readonly name: string;

  /** Приоритет выполнения (меньше = выше приоритет) */
  readonly priority: number;

  /** Описание формата для документации */
  readonly description: string;

  /**
   * Проверяет, может ли стратегия распарсить данную строку
   * @param line - Строка для проверки
   * @returns true если стратегия может распарсить строку
   */
  canParse(line: string): boolean;

  /**
   * Парсит строку и возвращает результат
   * @param line - Строка для парсинга
   * @returns Объект с id и name или null если парсинг не удался
   */
  parse(line: string): { id: number | null; name: string | null } | null;
}