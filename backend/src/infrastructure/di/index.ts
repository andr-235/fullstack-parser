/**
 * @fileoverview Composition Root - точка входа для DI
 *
 * Создает и экспортирует глобальный экземпляр DI Container.
 */

import { Container } from './Container';
import logger from '@infrastructure/utils/logger';

/**
 * Глобальный DI Container
 */
let container: Container | null = null;

/**
 * Инициализирует DI Container
 */
export function initializeContainer(vkAccessToken: string): Container {
  if (container) {
    logger.warn('DI Container already initialized');
    return container;
  }

  if (!vkAccessToken) {
    throw new Error('VK Access Token is required for DI Container initialization');
  }

  container = new Container(vkAccessToken);
  logger.info('DI Container initialized successfully');

  return container;
}

/**
 * Получает глобальный DI Container
 */
export function getContainer(): Container {
  if (!container) {
    throw new Error('DI Container not initialized. Call initializeContainer() first.');
  }

  return container;
}

/**
 * Уничтожает DI Container и освобождает ресурсы
 */
export async function disposeContainer(): Promise<void> {
  if (!container) {
    logger.warn('DI Container already disposed or not initialized');
    return;
  }

  await container.dispose();
  container = null;
  logger.info('DI Container disposed successfully');
}

// Экспортируем Container класс для типизации
export { Container } from './Container';
