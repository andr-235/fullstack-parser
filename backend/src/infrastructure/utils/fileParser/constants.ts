/**
 * Константы для парсера файлов с группами VK
 */
export const FILE_PARSER_CONSTANTS = {
  /** Максимальный размер файла в MB */
  MAX_FILE_SIZE_MB: 10,

  /** Разрешенные расширения файлов */
  ALLOWED_EXTENSIONS: ['.txt'] as const,

  /** Количество групп в sample для логирования */
  SAMPLE_GROUPS_COUNT: 5,

  /** Базовый URL VK */
  VK_BASE_URL: 'https://vk.com',

  /** Кодировка файла по умолчанию */
  DEFAULT_ENCODING: 'utf-8' as BufferEncoding
} as const;