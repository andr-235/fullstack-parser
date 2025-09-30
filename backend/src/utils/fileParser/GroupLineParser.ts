import { ValidationError } from '@/utils/errors';
import {
  GroupParsingStrategy,
  UrlClubStrategy,
  UrlScreenNameStrategy,
  NegativeIdStrategy,
  PositiveIdStrategy,
  ScreenNameStrategy
} from './strategies';

/**
 * Стратегии парсинга по умолчанию в порядке приоритета
 */
export const defaultStrategies: GroupParsingStrategy[] = [
  new UrlClubStrategy(),
  new UrlScreenNameStrategy(),
  new NegativeIdStrategy(),
  new PositiveIdStrategy(),
  new ScreenNameStrategy()
];

/**
 * Парсер строк с VK группами использующий паттерн Strategy.
 * Позволяет гибко расширять поддерживаемые форматы через добавление новых стратегий.
 */
export class GroupLineParser {
  private strategies: GroupParsingStrategy[];

  /**
   * @param strategies - Массив стратегий парсинга (по умолчанию используются стандартные)
   */
  constructor(strategies: GroupParsingStrategy[] = defaultStrategies) {
    this.strategies = [...strategies].sort((a, b) => a.priority - b.priority);
  }

  /**
   * Парсит строку используя зарегистрированные стратегии
   * @param line - Строка для парсинга
   * @param lineNumber - Номер строки в файле (для ошибок)
   * @returns Объект с id и name группы
   * @throws {ValidationError} Если ни одна стратегия не смогла распарсить строку
   */
  parse(line: string, lineNumber: number): { id: number | null; name: string | null; strategyName?: string } {
    for (const strategy of this.strategies) {
      if (strategy.canParse(line)) {
        const result = strategy.parse(line);
        if (result) {
          return { ...result, strategyName: strategy.name };
        }
      }
    }

    // Если ни одна стратегия не сработала - выбрасываем ValidationError
    throw new ValidationError('Invalid group format')
      .addFieldError(
        `line_${lineNumber}`,
        'Line does not match any supported VK group format',
        line,
        'GROUP_FORMAT'
      );
  }

  /**
   * Добавляет кастомную стратегию парсинга
   * Автоматически сортирует стратегии по приоритету
   * @param strategy - Новая стратегия для добавления
   */
  addStrategy(strategy: GroupParsingStrategy): void {
    this.strategies.push(strategy);
    this.strategies.sort((a, b) => a.priority - b.priority);
  }

  /**
   * Возвращает список всех зарегистрированных стратегий
   */
  getStrategies(): readonly GroupParsingStrategy[] {
    return [...this.strategies];
  }

  /**
   * Удаляет стратегию по имени
   * @param name - Имя стратегии для удаления
   * @returns true если стратегия была удалена
   */
  removeStrategy(name: string): boolean {
    const initialLength = this.strategies.length;
    this.strategies = this.strategies.filter(s => s.name !== name);
    return this.strategies.length < initialLength;
  }
}