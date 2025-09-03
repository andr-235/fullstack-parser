// Конфигурация приложения
export const config = {
  api: {
    // В Docker окружении используем пустой baseUrl - запросы пойдут через Nginx
    baseUrl: process.env.NEXT_PUBLIC_API_URL || '',
    timeout: 10000,
  },
  app: {
    name: 'Парсер комментариев VK',
    description: 'Современное веб-приложение для парсинга и анализа комментариев VK',
    version: '1.0.0',
  },
} as const

// Legacy export for backward compatibility
export const APP_CONFIG = config.app
