/**
 * @fileoverview Unit тесты для Group Entity
 *
 * Тестирует бизнес-логику и инварианты Group Entity.
 */

import { Group, VkId, GroupId, GroupStatus } from '@domain/index';
import { InvariantViolationError } from '@domain/errors/DomainError';

describe('Group Entity', () => {
  describe('create', () => {
    it('должен создать валидную группу', () => {
      // Arrange & Act
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123'
      });

      // Assert
      expect(group).toBeDefined();
      expect(group.name).toBe('Test Group');
      expect(group.vkId.value).toBe(123456789);
      expect(group.status.isValid()).toBe(true);
    });

    it('должен выбросить ошибку при пустом имени', () => {
      // Arrange & Act & Assert
      expect(() => {
        Group.create({
          vkId: VkId.create(123456789),
          name: '',
          screenName: 'testgroup',
          photo50: null,
          membersCount: 1000,
          isClosed: 0,
          description: null,
          status: GroupStatus.valid(),
          taskId: 'task-123'
        });
      }).toThrow(InvariantViolationError);
    });

    it('должен выбросить ошибку при слишком длинном имени', () => {
      // Arrange
      const longName = 'a'.repeat(256);

      // Act & Assert
      expect(() => {
        Group.create({
          vkId: VkId.create(123456789),
          name: longName,
          screenName: 'testgroup',
          photo50: null,
          membersCount: 1000,
          isClosed: 0,
          description: null,
          status: GroupStatus.valid(),
          taskId: 'task-123'
        });
      }).toThrow(InvariantViolationError);
    });

    it('должен автоматически установить uploadedAt', () => {
      // Arrange
      const beforeCreate = new Date();

      // Act
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123'
      });

      const afterCreate = new Date();

      // Assert
      expect(group.uploadedAt.getTime()).toBeGreaterThanOrEqual(beforeCreate.getTime());
      expect(group.uploadedAt.getTime()).toBeLessThanOrEqual(afterCreate.getTime());
    });
  });

  describe('restore', () => {
    it('должен восстановить группу из персистентного состояния', () => {
      // Arrange
      const uploadedAt = new Date('2025-01-01T00:00:00Z');

      // Act
      const group = Group.restore({
        id: GroupId.create(1),
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123',
        uploadedAt
      });

      // Assert
      expect(group.id.value).toBe(1);
      expect(group.uploadedAt).toEqual(uploadedAt);
    });
  });

  describe('markAsInvalid', () => {
    it('должен пометить группу как невалидную', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123'
      });

      // Act
      group.markAsInvalid('Group is closed');

      // Assert
      expect(group.status.isInvalid()).toBe(true);
      expect(group.status.reason).toBe('Group is closed');
    });
  });

  describe('markAsDuplicate', () => {
    it('должен пометить группу как дубликат', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123'
      });

      // Act
      group.markAsDuplicate();

      // Assert
      expect(group.status.isDuplicate()).toBe(true);
    });
  });

  describe('updateName', () => {
    it('должен обновить имя группы', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Old Name',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123'
      });

      // Act
      group.updateName('New Name');

      // Assert
      expect(group.name).toBe('New Name');
    });

    it('должен выбросить ошибку при попытке установить пустое имя', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Old Name',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123'
      });

      // Act & Assert
      expect(() => {
        group.updateName('');
      }).toThrow(InvariantViolationError);
    });
  });

  describe('updateVkInfo', () => {
    it('должен обновить информацию из VK API', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Old Name',
        screenName: 'oldscreen',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123'
      });

      // Act
      group.updateVkInfo({
        name: 'New Name',
        screenName: 'newscreen',
        photo50: 'https://example.com/photo.jpg',
        membersCount: 2000,
        description: 'New description'
      });

      // Assert
      expect(group.name).toBe('New Name');
      expect(group.screenName).toBe('newscreen');
      expect(group.photo50).toBe('https://example.com/photo.jpg');
      expect(group.membersCount).toBe(2000);
      expect(group.description).toBe('New description');
    });
  });

  describe('canBeProcessed', () => {
    it('должен вернуть true для валидной группы', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123'
      });

      // Act & Assert
      expect(group.canBeProcessed()).toBe(true);
    });

    it('должен вернуть false для невалидной группы', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.invalid('Closed'),
        taskId: 'task-123'
      });

      // Act & Assert
      expect(group.canBeProcessed()).toBe(false);
    });

    it('должен вернуть false для дубликата', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.duplicate(),
        taskId: 'task-123'
      });

      // Act & Assert
      expect(group.canBeProcessed()).toBe(false);
    });
  });

  describe('toPersistence', () => {
    it('должен преобразовать Entity в формат для сохранения', () => {
      // Arrange
      const group = Group.restore({
        id: GroupId.create(1),
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: 'https://example.com/photo.jpg',
        membersCount: 5000,
        isClosed: 1,
        description: 'Test description',
        status: GroupStatus.valid(),
        taskId: 'task-456',
        uploadedAt: new Date('2025-01-15T10:30:00Z')
      });

      // Act
      const persistence = group.toPersistence();

      // Assert
      expect(persistence).toEqual({
        id: 1,
        vk_id: 123456789,
        name: 'Test Group',
        screen_name: 'testgroup',
        photo_50: 'https://example.com/photo.jpg',
        members_count: 5000,
        is_closed: 1,
        description: 'Test description',
        status: 'valid',
        status_reason: null,
        task_id: 'task-456',
        uploaded_at: new Date('2025-01-15T10:30:00Z')
      });
    });

    it('должен включить status_reason для невалидной группы', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.invalid('Group not found'),
        taskId: 'task-123'
      });

      // Act
      const persistence = group.toPersistence();

      // Assert
      expect(persistence.status).toBe('invalid');
      expect(persistence.status_reason).toBe('Group not found');
    });
  });

  describe('getVkUrl', () => {
    it('должен вернуть URL группы по VK ID', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: null,
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123'
      });

      // Act
      const url = group.getVkUrl();

      // Assert
      expect(url).toBe('https://vk.com/club123456789');
    });

    it('должен вернуть URL по screenName если он есть', () => {
      // Arrange
      const group = Group.create({
        vkId: VkId.create(123456789),
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: null,
        membersCount: 1000,
        isClosed: 0,
        description: null,
        status: GroupStatus.valid(),
        taskId: 'task-123'
      });

      // Act
      const url = group.getVkUrl();

      // Assert
      expect(url).toBe('https://vk.com/testgroup');
    });
  });
});
