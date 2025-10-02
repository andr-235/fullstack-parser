/**
 * @fileoverview Infrastructure Layer
 *
 * Экспорт всех Infrastructure адаптеров.
 * Infrastructure Layer содержит реализации интерфейсов Domain Layer.
 */

// Database Repositories
export { PrismaGroupsRepository } from './database/repositories/PrismaGroupsRepository';

// External Services
export { VkApiAdapter } from './external-services/vk-api/VkApiAdapter';
export { FileParserAdapter } from './external-services/file-parser/FileParserAdapter';

// Storage
export { RedisTaskStorageAdapter } from './storage/RedisTaskStorageAdapter';
