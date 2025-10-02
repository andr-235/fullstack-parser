/**
 * @fileoverview Unit тесты для GetGroupsUseCase
 */

import { GetGroupsUseCase } from '@application/use-cases/groups/GetGroupsUseCase';
import { IGroupsRepository } from '@domain/repositories/IGroupsRepository';
import { Group, VkId, GroupId, GroupStatus } from '@domain/index';

describe('GetGroupsUseCase', () => {
  let useCase: GetGroupsUseCase;
  let mockGroupsRepo: jest.Mocked<IGroupsRepository>;

  beforeEach(() => {
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

    useCase = new GetGroupsUseCase(mockGroupsRepo);
  });

  describe('execute', () => {
    it('должен вернуть список групп с пагинацией', async () => {
      // Arrange
      const mockGroups = [
        Group.restore({
          id: GroupId.create(1),
          vkId: VkId.create(123456789),
          name: 'Test Group 1',
          screenName: 'test1',
          photo50: null,
          membersCount: 1000,
          isClosed: 0,
          description: null,
          status: GroupStatus.valid(),
          taskId: 'task-123',
          uploadedAt: new Date('2025-01-01')
        }),
        Group.restore({
          id: GroupId.create(2),
          vkId: VkId.create(987654321),
          name: 'Test Group 2',
          screenName: 'test2',
          photo50: null,
          membersCount: 2000,
          isClosed: 0,
          description: null,
          status: GroupStatus.valid(),
          taskId: 'task-123',
          uploadedAt: new Date('2025-01-02')
        })
      ];

      mockGroupsRepo.findAll.mockResolvedValue({
        groups: mockGroups,
        total: 2,
        hasMore: false
      });

      const input = {
        limit: 10,
        offset: 0
      };

      // Act
      const result = await useCase.execute(input);

      // Assert
      expect(result.groups).toHaveLength(2);
      expect(result.total).toBe(2);
      expect(result.groups[0]).toMatchObject({
        id: 1,
        vkId: 123456789,
        name: 'Test Group 1',
        screenName: 'test1',
        status: 'valid'
      });
    });

    it('должен применить фильтр по статусу', async () => {
      // Arrange
      mockGroupsRepo.findAll.mockResolvedValue({
        groups: [],
        total: 0,
        hasMore: false
      });

      const input = {
        limit: 10,
        offset: 0,
        status: 'valid' as const
      };

      // Act
      await useCase.execute(input);

      // Assert
      expect(mockGroupsRepo.findAll).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'valid'
        })
      );
    });

    it('должен применить поиск по имени', async () => {
      // Arrange
      mockGroupsRepo.findAll.mockResolvedValue({
        groups: [],
        total: 0,
        hasMore: false
      });

      const input = {
        limit: 10,
        offset: 0,
        search: 'test'
      };

      // Act
      await useCase.execute(input);

      // Assert
      expect(mockGroupsRepo.findAll).toHaveBeenCalledWith(
        expect.objectContaining({
          search: 'test'
        })
      );
    });

    it('должен применить сортировку', async () => {
      // Arrange
      mockGroupsRepo.findAll.mockResolvedValue({
        groups: [],
        total: 0,
        hasMore: false
      });

      const input = {
        limit: 10,
        offset: 0,
        sortBy: 'name',
        sortOrder: 'DESC' as const
      };

      // Act
      await useCase.execute(input);

      // Assert
      expect(mockGroupsRepo.findAll).toHaveBeenCalledWith(
        expect.objectContaining({
          sortBy: 'name',
          sortOrder: 'DESC'
        })
      );
    });

    it('должен вернуть пустой список если групп нет', async () => {
      // Arrange
      mockGroupsRepo.findAll.mockResolvedValue({
        groups: [],
        total: 0,
        hasMore: false
      });

      const input = {
        limit: 10,
        offset: 0
      };

      // Act
      const result = await useCase.execute(input);

      // Assert
      expect(result.groups).toHaveLength(0);
      expect(result.total).toBe(0);
    });

    it('должен корректно преобразовать Group Entity в GroupDto', async () => {
      // Arrange
      const mockGroup = Group.restore({
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

      mockGroupsRepo.findAll.mockResolvedValue({
        groups: [mockGroup],
        total: 1,
        hasMore: false
      });

      const input = {
        limit: 10,
        offset: 0
      };

      // Act
      const result = await useCase.execute(input);

      // Assert
      const dto = result.groups[0];
      expect(dto).toMatchObject({
        id: 1,
        vkId: 123456789,
        name: 'Test Group',
        screenName: 'testgroup',
        photo50: 'https://example.com/photo.jpg',
        membersCount: 5000,
        isClosed: 1,
        description: 'Test description',
        status: 'valid',
        uploadedAt: '2025-01-15T10:30:00.000Z',
        vkUrl: 'https://vk.com/club123456789'
      });
    });
  });
});
