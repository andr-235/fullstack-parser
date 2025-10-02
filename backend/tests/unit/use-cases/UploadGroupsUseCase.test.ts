/**
 * @fileoverview Unit тесты для UploadGroupsUseCase
 *
 * Тестирует бизнес-логику загрузки групп согласно Clean Architecture.
 */

import { UploadGroupsUseCase } from '@application/use-cases/groups/UploadGroupsUseCase';
import { IGroupsRepository } from '@domain/repositories/IGroupsRepository';
import { IVkApiRepository } from '@domain/repositories/IVkApiRepository';
import { ITaskStorageRepository } from '@domain/repositories/ITaskStorageRepository';
import { IFileParser } from '@domain/repositories/IFileParser';
import { Group, VkId, GroupStatus } from '@domain/index';

describe('UploadGroupsUseCase', () => {
  let useCase: UploadGroupsUseCase;
  let mockGroupsRepo: jest.Mocked<IGroupsRepository>;
  let mockVkApiRepo: jest.Mocked<IVkApiRepository>;
  let mockTaskStorage: jest.Mocked<ITaskStorageRepository>;
  let mockFileParser: jest.Mocked<IFileParser>;

  beforeEach(() => {
    // Создаем mock репозиториев
    mockGroupsRepo = {
      save: jest.fn(),
      saveMany: jest.fn(),
      findById: jest.fn(),
      findByVkId: jest.fn(),
      findAll: jest.fn(),
      delete: jest.fn(),
      deleteMany: jest.fn(),
      exists: jest.fn(),
      count: jest.fn(),
      getStatistics: jest.fn()
    } as any;

    mockVkApiRepo = {
      getGroupInfo: jest.fn(),
      getGroupsInfo: jest.fn(),
      isGroupAccessible: jest.fn(),
      getPost: jest.fn(),
      getPostComments: jest.fn(),
      isTokenValid: jest.fn(),
      getCurrentUser: jest.fn()
    } as any;

    mockTaskStorage = {
      saveTask: jest.fn(),
      getTask: jest.fn(),
      updateTaskStatus: jest.fn(),
      updateTaskProgress: jest.fn(),
      deleteTask: jest.fn(),
      deleteTasksByPattern: jest.fn(),
      findTasksByPattern: jest.fn(),
      taskExists: jest.fn(),
      extendTaskTTL: jest.fn(),
      cleanupOldTasks: jest.fn()
    } as any;

    mockFileParser = {
      parseGroupsFile: jest.fn(),
      validateFile: jest.fn()
    } as any;

    useCase = new UploadGroupsUseCase(
      mockGroupsRepo,
      mockVkApiRepo,
      mockTaskStorage,
      mockFileParser
    );
  });

  describe('execute', () => {
    it('должен успешно создать задачу загрузки групп', async () => {
      // Arrange
      const fileBuffer = Buffer.from('test content');
      const input = {
        file: fileBuffer,
        encoding: 'utf-8' as BufferEncoding,
        fileName: 'test.txt'
      };

      mockFileParser.validateFile.mockResolvedValue({
        isValid: true,
        errors: []
      });

      mockFileParser.parseGroupsFile.mockResolvedValue({
        groups: [
          { id: 123456789, name: 'Test Group 1' },
          { id: 987654321, name: 'Test Group 2' }
        ],
        errors: []
      });

      mockTaskStorage.saveTask.mockResolvedValue();

      // Act
      const result = await useCase.execute(input);

      // Assert
      expect(result).toHaveProperty('taskId');
      expect(result).toHaveProperty('totalGroups', 2);
      expect(result).toHaveProperty('message');
      expect(mockFileParser.validateFile).toHaveBeenCalledWith(fileBuffer);
      expect(mockFileParser.parseGroupsFile).toHaveBeenCalledWith(fileBuffer, 'utf-8');
      expect(mockTaskStorage.saveTask).toHaveBeenCalled();
    });

    it('должен выбросить ошибку при невалидном файле', async () => {
      // Arrange
      const fileBuffer = Buffer.from('invalid content');
      const input = {
        file: fileBuffer,
        encoding: 'utf-8' as BufferEncoding,
        fileName: 'invalid.txt'
      };

      mockFileParser.validateFile.mockResolvedValue({
        isValid: false,
        errors: ['Invalid file format']
      });

      // Act & Assert
      await expect(useCase.execute(input)).rejects.toThrow('File validation failed');
      expect(mockFileParser.parseGroupsFile).not.toHaveBeenCalled();
      expect(mockTaskStorage.saveTask).not.toHaveBeenCalled();
    });

    it('должен обработать ошибки парсинга файла', async () => {
      // Arrange
      const fileBuffer = Buffer.from('test content');
      const input = {
        file: fileBuffer,
        encoding: 'utf-8' as BufferEncoding,
        fileName: 'test.txt'
      };

      mockFileParser.validateFile.mockResolvedValue({
        isValid: true,
        errors: []
      });

      mockFileParser.parseGroupsFile.mockResolvedValue({
        groups: [
          { id: 123456789, name: 'Test Group 1' }
        ],
        errors: ['Line 5: Invalid format', 'Line 10: Missing ID']
      });

      mockTaskStorage.saveTask.mockResolvedValue();

      // Act
      const result = await useCase.execute(input);

      // Assert
      expect(result.totalGroups).toBe(1);
      expect(mockTaskStorage.saveTask).toHaveBeenCalled();

      // Проверяем, что задача содержит ошибки парсинга
      const taskData = (mockTaskStorage.saveTask as jest.Mock).mock.calls[0][1];
      expect(taskData.errors).toContain('Line 5: Invalid format');
      expect(taskData.errors).toContain('Line 10: Missing ID');
    });

    it('должен создать задачу с корректными метаданными', async () => {
      // Arrange
      const fileBuffer = Buffer.from('test content');
      const fileName = 'my-groups.txt';
      const input = {
        file: fileBuffer,
        encoding: 'utf-8' as BufferEncoding,
        fileName
      };

      mockFileParser.validateFile.mockResolvedValue({
        isValid: true,
        errors: []
      });

      mockFileParser.parseGroupsFile.mockResolvedValue({
        groups: [
          { id: 123, name: 'Group 1' },
          { id: 456, name: 'Group 2' },
          { id: 789, name: 'Group 3' }
        ],
        errors: []
      });

      mockTaskStorage.saveTask.mockResolvedValue();

      // Act
      await useCase.execute(input);

      // Assert
      const [[taskId, taskData]] = (mockTaskStorage.saveTask as jest.Mock).mock.calls;

      expect(taskId).toBeTruthy();
      expect(taskData).toMatchObject({
        taskId: expect.any(String),
        status: 'pending',
        total: 3,
        fileName,
        fileSize: fileBuffer.length,
        createdAt: expect.any(Date)
      });
    });
  });

  describe('асинхронная обработка групп', () => {
    it('должен обработать группы через VK API', async () => {
      // Arrange
      const fileBuffer = Buffer.from('test');
      const input = {
        file: fileBuffer,
        encoding: 'utf-8' as BufferEncoding,
        fileName: 'test.txt'
      };

      mockFileParser.validateFile.mockResolvedValue({
        isValid: true,
        errors: []
      });

      mockFileParser.parseGroupsFile.mockResolvedValue({
        groups: [
          { id: 123456789, name: 'Test Group' }
        ],
        errors: []
      });

      mockTaskStorage.saveTask.mockResolvedValue();
      mockTaskStorage.updateTaskStatus.mockResolvedValue();

      mockVkApiRepo.getGroupsInfo.mockResolvedValue({
        successful: [
          {
            id: 123456789,
            name: 'Test Group',
            screenName: 'test_group',
            photo50: null,
            membersCount: 1000,
            isClosed: 0,
            description: null
          }
        ],
        failed: []
      });

      mockGroupsRepo.exists.mockResolvedValue(false);
      mockGroupsRepo.saveMany.mockResolvedValue();

      // Act
      await useCase.execute(input);

      // Даем время на асинхронную обработку
      await new Promise(resolve => setTimeout(resolve, 100));

      // Assert
      expect(mockVkApiRepo.getGroupsInfo).toHaveBeenCalled();
      expect(mockGroupsRepo.saveMany).toHaveBeenCalled();
    });
  });
});
