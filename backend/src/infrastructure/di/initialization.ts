import { initializeContainer } from '@infrastructure/di';
import logger from '@infrastructure/utils/logger';

/**
 * Инициализация DI Container приложения
 *
 * Выполняет настройку и проверку зависимостей при старте приложения
 */
export const initializeDIContainer = (): void => {
  const vkAccessToken = process.env.VK_ACCESS_TOKEN;

  if (!vkAccessToken) {
    logger.error('VK_ACCESS_TOKEN not found in environment variables');
    throw new Error('VK_ACCESS_TOKEN is required');
  }

  try {
    initializeContainer(vkAccessToken);
    logger.info('DI Container initialized successfully');
  } catch (error) {
    logger.error('Failed to initialize DI Container', {
      error: error instanceof Error ? error.message : String(error)
    });
    throw error;
  }
};
