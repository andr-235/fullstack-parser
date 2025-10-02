/**
 * @fileoverview Domain Value Objects
 *
 * Экспорт всех Value Objects из Domain Layer.
 *
 * VALUE OBJECT ПРИНЦИПЫ:
 * - Неизменяемые (immutable)
 * - Сравниваются по значению
 * - Валидация в конструкторе
 * - Не имеют идентификатора
 * - Могут содержать бизнес-логику
 */

export { VkId } from './VkId';
export { GroupId } from './GroupId';
export { TaskId } from './TaskId';
export { GroupStatus } from './GroupStatus';
