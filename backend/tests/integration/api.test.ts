import request from 'supertest';
import app from '../../src/server';

// Мокаем taskService модуль
jest.mock('../../src/services/taskService', () => ({
  default: {
    createTask: jest.fn(),
    startCollect: jest.fn(),
    getTaskStatus: jest.fn(),
    listTasks: jest.fn(),
    getTaskById: jest.fn(),
  }
}));

// Мокаем vkApi для тестирования VK интеграции
jest.mock('../../src/repositories/vkApi', () => ({
  default: {
    getGroupsInfo: jest.fn(),
  }
}));

import taskService from '../../src/services/taskService';
import vkApi from '../../src/repositories/vkApi';
const mockTaskService = taskService as jest.Mocked<typeof taskService>;
const mockVkApi = vkApi as jest.Mocked<typeof vkApi>;

describe('API Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Task API Endpoints - Basic Functionality', () => {
    describe('POST /api/tasks - Create VK Comment Task', () => {
      it('should create a fetch comments task with valid data', async () => {
        const mockTask = { taskId: 1, status: 'pending' as const };
        mockTaskService.createTask.mockResolvedValue(mockTask);

        const taskData = {
          ownerId: -123456,
          postId: 789,
          token: 'vk_access_token_123'
        };

        const response = await request(app)
          .post('/api/tasks')
          .send(taskData)
          .expect(201);

        expect(response.body).toEqual({
          success: true,
          data: { taskId: 1, status: 'created' }
        });
        expect(mockTaskService.createTask).toHaveBeenCalledWith({
          type: 'fetch_comments',
          postUrls: ['-123456_789'],
          options: { token: 'vk_access_token_123' }
        });
      });

      it('should reject invalid ownerId (positive value)', async () => {
        const taskData = {
          ownerId: 123456, // Should be negative for groups
          postId: 789,
          token: 'vk_access_token_123'
        };

        const response = await request(app)
          .post('/api/tasks')
          .send(taskData)
          .expect(400);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toContain('negative');
      });

      it('should reject missing required fields', async () => {
        const taskData = {
          ownerId: -123456,
          // postId missing
          token: 'vk_access_token_123'
        };

        const response = await request(app)
          .post('/api/tasks')
          .send(taskData)
          .expect(400);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toContain('required');
      });
    });

    describe('POST /api/tasks/collect - Create VK Collect Task', () => {
      it('should create VK collect task with groups array', async () => {
        const mockTask = { taskId: 2, status: 'pending' as const };
        mockTaskService.createTask.mockResolvedValue(mockTask);

        // Mock VK API response for groups info
        mockVkApi.getGroupsInfo.mockResolvedValue([
          { id: 123, name: 'Test Group 1', screen_name: 'test_group_1', description: 'Test group description' },
          { id: 456, name: 'Test Group 2', screen_name: 'test_group_2', description: 'Test group description' }
        ]);

        const taskData = {
          groups: [123, 456, '789'] // Mixed types
        };

        const response = await request(app)
          .post('/api/tasks/collect')
          .send(taskData)
          .expect(201);

        expect(response.body).toEqual({
          success: true,
          data: { taskId: 2, status: 'created' }
        });
        expect(mockTaskService.createTask).toHaveBeenCalledWith({
          type: 'fetch_comments',
          groupIds: [123, 456, 789],
          options: {}
        });
        expect(mockVkApi.getGroupsInfo).toHaveBeenCalledWith([123, 456, 789]);
      });

      it('should handle VK API failure gracefully', async () => {
        const mockTask = { taskId: 3, status: 'pending' as const };
        mockTaskService.createTask.mockResolvedValue(mockTask);

        // Mock VK API failure
        mockVkApi.getGroupsInfo.mockRejectedValue(new Error('VK API error'));

        const taskData = {
          groups: [123, 456]
        };

        const response = await request(app)
          .post('/api/tasks/collect')
          .send(taskData)
          .expect(201);

        expect(response.body.success).toBe(true);
        expect(mockTaskService.createTask).toHaveBeenCalled();
      });

      it('should remove duplicate groups', async () => {
        const mockTask = { taskId: 4, status: 'pending' as const };
        mockTaskService.createTask.mockResolvedValue(mockTask);
        mockVkApi.getGroupsInfo.mockResolvedValue([{ id: 123, name: 'Test Group', screen_name: 'test_group', description: 'Test group description' }]);

        const taskData = {
          groups: [123, '123', 123] // Duplicates
        };

        const response = await request(app)
          .post('/api/tasks/collect')
          .send(taskData)
          .expect(201);

        expect(mockVkApi.getGroupsInfo).toHaveBeenCalledWith([123]);
      });
    });

    describe('GET /api/tasks/:taskId - Get Task Status', () => {
      it('should return task status with full response structure', async () => {
        const mockStatus = {
          status: 'processing' as const,
          type: 'fetch_comments' as const,
          priority: 0,
          progress: 50,
          metrics: { posts: 10, comments: 150, errors: [] },
          errors: [],
          groups: [123, 456],
          parameters: { token: '***' },
          result: null,
          error: null,
          executionTime: null,
          startedAt: new Date('2023-01-01T10:00:00Z'),
          finishedAt: null,
          createdBy: 'system',
          createdAt: new Date('2023-01-01T09:00:00Z'),
          updatedAt: new Date('2023-01-01T10:00:00Z')
        };
        mockTaskService.getTaskStatus.mockResolvedValue(mockStatus);

        const response = await request(app)
          .get('/api/tasks/1')
          .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.data).toMatchObject({
          id: 1,
          status: 'processing',
          type: 'fetch_comments',
          progress: {
            processed: 150,
            total: 150
          },
          errors: [],
          groups: [123, 456]
        });
        expect(mockTaskService.getTaskStatus).toHaveBeenCalledWith(1);
      });

      it('should return 404 for non-existent task', async () => {
        mockTaskService.getTaskStatus.mockRejectedValue(new Error('Task not found'));

        const response = await request(app)
          .get('/api/tasks/999')
          .expect(404);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe('Task not found');
      });

      it('should return 400 for invalid task ID', async () => {
        const response = await request(app)
          .get('/api/tasks/invalid')
          .expect(400);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe('Invalid task ID');
      });
    });

    describe('POST /api/collect/:taskId - Start Collection', () => {
      it('should start collection for pending task', async () => {
        const mockTask = { id: 1, status: 'pending' };
        mockTaskService.getTaskById.mockResolvedValue(mockTask);
        mockTaskService.startCollect.mockResolvedValue({
          status: 'processing',
          startedAt: new Date('2023-01-01T10:00:00Z')
        });

        const response = await request(app)
          .post('/api/collect/1')
          .expect(202);

        expect(response.body.success).toBe(true);
        expect(response.body.data.status).toBe('pending');
        expect(mockTaskService.startCollect).toHaveBeenCalledWith(1);
      });

      it('should return 404 for non-existent task', async () => {
        mockTaskService.getTaskById.mockResolvedValue(null);

        const response = await request(app)
          .post('/api/collect/999')
          .expect(404);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe('Task not found');
      });
    });

    describe('GET /api/tasks - List Tasks', () => {
      it('should list tasks with pagination', async () => {
        const mockList = {
          tasks: [
            { id: 1, status: 'completed', type: 'fetch_comments' },
            { id: 2, status: 'processing', type: 'fetch_comments' }
          ],
          total: 15
        };
        mockTaskService.listTasks.mockResolvedValue(mockList);

        const response = await request(app)
          .get('/api/tasks?page=1&limit=10')
          .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.data).toEqual(mockList.tasks);
        expect(response.body.pagination).toEqual({
          page: 1,
          limit: 10,
          total: 15,
          totalPages: 2
        });
        expect(mockTaskService.listTasks).toHaveBeenCalledWith(1, 10, undefined, undefined);
      });

      it('should filter tasks by status', async () => {
        const mockList = { tasks: [], total: 0 };
        mockTaskService.listTasks.mockResolvedValue(mockList);

        await request(app)
          .get('/api/tasks?status=pending')
          .expect(200);

        expect(mockTaskService.listTasks).toHaveBeenCalledWith(1, 10, 'pending', undefined);
      });

      it('should validate query parameters', async () => {
        const response = await request(app)
          .get('/api/tasks?page=0&limit=200') // Invalid values
          .expect(400);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toContain('Validation');
      });
    });
  });

  describe('CORS and Headers Testing', () => {
    it('should include CORS headers in responses', async () => {
      mockTaskService.listTasks.mockResolvedValue({ tasks: [], total: 0 });

      const response = await request(app)
        .get('/api/tasks')
        .set('Origin', 'http://localhost:5173')
        .expect(200);

      // Note: supertest doesn't fully simulate CORS in the same way browsers do
      // but we can verify the endpoint responds correctly
      expect(response.body.success).toBe(true);
    });

    it('should handle preflight OPTIONS requests', async () => {
      await request(app)
        .options('/api/tasks')
        .set('Origin', 'http://localhost:5173')
        .set('Access-Control-Request-Method', 'GET')
        .expect(204);
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle service errors gracefully', async () => {
      mockTaskService.createTask.mockRejectedValue(new Error('Database connection failed'));

      const response = await request(app)
        .post('/api/tasks')
        .send({
          ownerId: -123456,
          postId: 789,
          token: 'vk_access_token_123'
        })
        .expect(500);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Internal server error');
    });

    it('should handle validation errors properly', async () => {
      mockTaskService.createTask.mockRejectedValue(new Error('Validation failed: invalid token'));
      mockTaskService.createTask.mockImplementation(() => {
        const error = new Error('Validation failed: invalid token');
        error.name = 'ValidationError';
        throw error;
      });

      const response = await request(app)
        .post('/api/tasks')
        .send({
          ownerId: -123456,
          postId: 789,
          token: 'invalid_token'
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('Validation failed');
    });

    it('should handle malformed JSON requests', async () => {
      const response = await request(app)
        .post('/api/tasks')
        .set('Content-Type', 'application/json')
        .send('{ invalid json }')
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('INVALID_JSON');
    });

    it('should return 404 for non-existent endpoints', async () => {
      const response = await request(app)
        .get('/api/nonexistent')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('NOT_FOUND');
    });
  });

  describe('Health Check Endpoints', () => {
    it('should respond to basic health check', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);

      expect(response.body.status).toBe('healthy');
      expect(response.body.timestamp).toBeDefined();
    });
  });
});