import request from 'supertest';
import app from '../../src/server';
import { performance } from 'perf_hooks';

// Mock dependencies for controlled testing
jest.mock('../../src/services/taskService', () => ({
  default: {
    createTask: jest.fn(),
    getTaskStatus: jest.fn(),
    getTaskById: jest.fn(),
    listTasks: jest.fn(),
    updateTaskStatus: jest.fn(),
  }
}));

jest.mock('../../src/repositories/vkApi', () => ({
  default: {
    getGroupsInfo: jest.fn(),
  }
}));

jest.mock('../../src/services/groupsService', () => ({
  default: {
    getAllGroups: jest.fn(),
    uploadGroups: jest.fn(),
  }
}));

import taskService from '../../src/services/taskService';
import vkApi from '../../src/repositories/vkApi';
import groupsService from '../../src/services/groupsService';

const mockTaskService = taskService as jest.Mocked<typeof taskService>;
const mockVkApi = vkApi as jest.Mocked<typeof vkApi>;
const mockGroupsService = groupsService as jest.Mocked<typeof groupsService>;

/**
 * API Response Format Standardization Testing Strategy
 * 
 * Цель: Валидация исправлений несогласованности форматов API ответов
 * 
 * Проблема:
 * - Некоторые endpoints возвращают { success: true, data: {...} }
 * - Другие endpoints возвращают прямые данные
 * - Frontend вынужден обрабатывать оба формата
 * 
 * Решение:
 * - Стандартизировать все API ответы к единому формату
 * - Реализовать middleware для автоматического обертывания
 * - Обновить frontend код для работы с стандартным форматом
 */
describe('API Response Format Standardization Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Определяем стандартный формат API response
  interface StandardApiResponse<T = any> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
    timestamp?: string;
    requestId?: string;
  }

  // Хелпер для проверки стандартного формата
  const validateStandardResponse = (response: any, expectSuccess: boolean = true): void => {
    expect(response.body).toHaveProperty('success');
    expect(response.body.success).toBe(expectSuccess);
    
    if (expectSuccess) {
      expect(response.body).toHaveProperty('data');
      expect(response.body.data).toBeDefined();
    } else {
      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toBeDefined();
    }
    
    // Опциональные поля для better debugging
    if (response.body.timestamp) {
      expect(new Date(response.body.timestamp)).toBeInstanceOf(Date);
    }
    
    console.log(`✅ Standard API format validated for ${expectSuccess ? 'success' : 'error'} response`);
  };

  describe('1. Task API Endpoints Standardization', () => {
    it('should return standardized format for POST /api/tasks (create task)', async () => {
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
      
      validateStandardResponse(response, true);
      
      // Проверяем специфичные поля для создания задачи
      expect(response.body.data).toHaveProperty('taskId', 1);
      expect(response.body.data).toHaveProperty('status', 'created');
      
      console.log('✅ STANDARDIZED: POST /api/tasks returns consistent format');
    });

    it('should return standardized format for POST /api/tasks/collect (VK collect task)', async () => {
      const mockTask = { taskId: 2, status: 'pending' as const };
      mockTaskService.createTask.mockResolvedValue(mockTask);
      
      mockVkApi.getGroupsInfo.mockResolvedValue([
        { id: 123, name: 'Test Group', screen_name: 'test_group', description: 'Test description' }
      ]);
      
      const taskData = { groups: [123] };
      
      const response = await request(app)
        .post('/api/tasks/collect')
        .send(taskData)
        .expect(201);
      
      validateStandardResponse(response, true);
      
      expect(response.body.data).toHaveProperty('taskId', 2);
      expect(response.body.data).toHaveProperty('status', 'created');
      
      console.log('✅ STANDARDIZED: POST /api/tasks/collect returns consistent format');
    });

    it('should return standardized format for GET /api/tasks/:id (task status)', async () => {
      const mockTaskStatus = {
        id: 1,
        status: 'processing' as const,
        type: 'fetch_comments' as const,
        priority: 0,
        progress: 50,
        metrics: { posts: 10, comments: 150, errors: [] },
        errors: [],
        groups: [123, 456],
        parameters: {},
        result: null,
        error: null,
        executionTime: null,
        startedAt: new Date('2023-01-01T10:00:00Z'),
        finishedAt: null,
        createdBy: 'system',
        createdAt: new Date('2023-01-01T09:00:00Z'),
        updatedAt: new Date('2023-01-01T10:00:00Z')
      };
      
      mockTaskService.getTaskStatus.mockResolvedValue(mockTaskStatus);
      
      const response = await request(app)
        .get('/api/tasks/1')
        .expect(200);
      
      validateStandardResponse(response, true);
      
      // Проверяем структуру данных задачи
      const taskData = response.body.data;
      expect(taskData).toHaveProperty('id', 1);
      expect(taskData).toHaveProperty('status', 'processing');
      expect(taskData).toHaveProperty('progress');
      expect(taskData.progress).toHaveProperty('processed');
      expect(taskData.progress).toHaveProperty('total');
      expect(taskData).toHaveProperty('groups');
      expect(taskData).toHaveProperty('startedAt');
      expect(taskData).toHaveProperty('finishedAt');
      
      console.log('✅ STANDARDIZED: GET /api/tasks/:id returns consistent format');
    });

    it('should return standardized format for GET /api/tasks (task list)', async () => {
      const mockTasks = [
        {
          id: 1,
          status: 'completed' as const,
          type: 'fetch_comments' as const,
          createdAt: new Date(),
          startedAt: new Date(),
          finishedAt: new Date(),
          progress: 100
        },
        {
          id: 2,
          status: 'pending' as const,
          type: 'vk_collect' as const,
          createdAt: new Date(),
          startedAt: null,
          finishedAt: null,
          progress: 0
        }
      ];
      
      mockTaskService.listTasks.mockResolvedValue({
        tasks: mockTasks,
        total: 2,
        page: 1,
        limit: 10
      });
      
      const response = await request(app)
        .get('/api/tasks')
        .expect(200);
      
      validateStandardResponse(response, true);
      
      // Проверяем структуру пагинации
      expect(response.body.data).toHaveProperty('tasks');
      expect(response.body.data).toHaveProperty('total', 2);
      expect(response.body.data).toHaveProperty('page', 1);
      expect(response.body.data).toHaveProperty('limit', 10);
      expect(response.body.data.tasks).toHaveLength(2);
      
      console.log('✅ STANDARDIZED: GET /api/tasks returns consistent paginated format');
    });
  });

  describe('2. Groups API Endpoints Standardization', () => {
    it('should return standardized format for GET /api/groups', async () => {
      const mockGroups = [
        {
          id: 123,
          name: 'Test Group 1',
          screen_name: 'test_group_1',
          description: 'Test description 1',
          members_count: 1000
        },
        {
          id: 456,
          name: 'Test Group 2',
          screen_name: 'test_group_2',
          description: 'Test description 2',
          members_count: 2000
        }
      ];
      
      mockGroupsService.getAllGroups.mockResolvedValue(mockGroups);
      
      const response = await request(app)
        .get('/api/groups')
        .expect(200);
      
      validateStandardResponse(response, true);
      
      expect(response.body.data).toHaveLength(2);
      expect(response.body.data[0]).toHaveProperty('id', 123);
      expect(response.body.data[0]).toHaveProperty('name', 'Test Group 1');
      
      console.log('✅ STANDARDIZED: GET /api/groups returns consistent format');
    });

    it('should return standardized format for POST /api/groups/upload', async () => {
      const mockUploadResult = {
        processed: 10,
        added: 8,
        updated: 2,
        errors: []
      };
      
      mockGroupsService.uploadGroups.mockResolvedValue(mockUploadResult);
      
      const response = await request(app)
        .post('/api/groups/upload')
        .attach('file', Buffer.from('test,csv,data'), 'groups.csv')
        .expect(200);
      
      validateStandardResponse(response, true);
      
      expect(response.body.data).toHaveProperty('processed', 10);
      expect(response.body.data).toHaveProperty('added', 8);
      expect(response.body.data).toHaveProperty('updated', 2);
      expect(response.body.data).toHaveProperty('errors');
      
      console.log('✅ STANDARDIZED: POST /api/groups/upload returns consistent format');
    });
  });

  describe('3. Error Response Standardization', () => {
    it('should return standardized error format for validation errors', async () => {
      const response = await request(app)
        .post('/api/tasks')
        .send({
          ownerId: 123456, // Неправильный - должен быть отрицательным
          postId: 789,
          token: 'vk_access_token_123'
        })
        .expect(400);
      
      validateStandardResponse(response, false);
      
      expect(response.body.error).toContain('negative');
      expect(response.body).not.toHaveProperty('data');
      
      console.log('✅ STANDARDIZED: Validation errors return consistent format');
    });

    it('should return standardized error format for not found errors', async () => {
      mockTaskService.getTaskStatus.mockRejectedValue(new Error('Task not found'));
      
      const response = await request(app)
        .get('/api/tasks/999999')
        .expect(404);
      
      validateStandardResponse(response, false);
      
      expect(response.body.error).toBe('Task not found');
      expect(response.body).not.toHaveProperty('data');
      
      console.log('✅ STANDARDIZED: Not found errors return consistent format');
    });

    it('should return standardized error format for server errors', async () => {
      mockTaskService.getTaskStatus.mockRejectedValue(new Error('Database connection failed'));
      
      const response = await request(app)
        .get('/api/tasks/1')
        .expect(500);
      
      validateStandardResponse(response, false);
      
      expect(response.body.error).toBe('Internal server error');
      expect(response.body).not.toHaveProperty('data');
      
      console.log('✅ STANDARDIZED: Server errors return consistent format');
    });
  });

  describe('4. Response Time and Performance Validation', () => {
    it('should validate response time for all standardized endpoints', async () => {
      const endpoints = [
        { method: 'GET', path: '/api/health', expectedStatus: 200 },
        { method: 'GET', path: '/api/health/detailed', expectedStatus: 200 }
      ];
      
      for (const endpoint of endpoints) {
        const startTime = performance.now();
        
        let response;
        if (endpoint.method === 'GET') {
          response = await request(app)
            .get(endpoint.path)
            .expect(endpoint.expectedStatus);
        }
        
        const responseTime = performance.now() - startTime;
        
        validateStandardResponse(response!, true);
        
        console.log(`⚡ ${endpoint.method} ${endpoint.path} responded in ${responseTime.toFixed(2)}ms`);
        expect(responseTime).toBeLessThan(500); // Ответ должен приходить быстро
      }
      
      console.log('✅ PERFORMANCE: All standardized endpoints respond quickly');
    });
  });

  describe('5. Frontend Compatibility Testing', () => {
    it('should validate that frontend can consistently parse all API responses', async () => {
      // Симулируем логику frontend парсинга
      const parseApiResponse = (response: any) => {
        // Старая логика (нужно убрать после стандартизации)
        // const data = response.data.data || response.data;
        
        // Новая логика (после стандартизации)
        if (!response.data || !response.data.success) {
          throw new Error(response.data?.error || 'API response error');
        }
        
        return response.data.data;
      };
      
      // Мокаем различные API ответы
      mockTaskService.getTaskStatus.mockResolvedValue({
        id: 1,
        status: 'processing',
        progress: 50
      });
      
      // Тестируем парсинг различных endpoints
      const taskResponse = await request(app).get('/api/tasks/1');
      
      expect(() => parseApiResponse(taskResponse)).not.toThrow();
      
      const parsedTaskData = parseApiResponse(taskResponse);
      expect(parsedTaskData).toHaveProperty('id', 1);
      expect(parsedTaskData).toHaveProperty('status', 'processing');
      
      console.log('✅ COMPATIBILITY: Frontend can consistently parse all standardized responses');
    });

    it('should validate error handling consistency across all endpoints', async () => {
      const errorTestCases = [
        {
          endpoint: '/api/tasks/invalid',
          expectedStatus: 400,
          expectedError: 'Invalid task ID'
        },
        {
          endpoint: '/api/tasks/999999',
          expectedStatus: 404,
          expectedError: 'Task not found',
          setupMock: () => mockTaskService.getTaskStatus.mockRejectedValue(new Error('Task not found'))
        }
      ];
      
      for (const testCase of errorTestCases) {
        if (testCase.setupMock) {
          testCase.setupMock();
        }
        
        const response = await request(app)
          .get(testCase.endpoint)
          .expect(testCase.expectedStatus);
        
        validateStandardResponse(response, false);
        expect(response.body.error).toBe(testCase.expectedError);
        
        console.log(`✅ ERROR HANDLING: ${testCase.endpoint} returns standardized error`);
      }
    });
  });

  describe('6. Backward Compatibility and Migration Testing', () => {
    it('should validate that existing frontend code can work with new standardized format', async () => {
      // Симуляция старого frontend кода, который ожидает response.data.data
      const legacyParseResponse = (response: any) => {
        // Логика из старого frontend кода
        return response.data.data || response.data;
      };
      
      mockTaskService.getTaskStatus.mockResolvedValue({
        id: 1,
        status: 'processing',
        progress: 50
      });
      
      const response = await request(app).get('/api/tasks/1');
      
      // Проверяем, что старый код все еще работает
      const legacyData = legacyParseResponse(response);
      expect(legacyData).toHaveProperty('id', 1);
      expect(legacyData).toHaveProperty('status', 'processing');
      
      console.log('✅ BACKWARD COMPATIBILITY: Legacy frontend code still works');
    });

    it('should provide migration path for frontend code', async () => {
      // Новая рекомендуемая логика
      const modernParseResponse = (response: any) => {
        if (!response.data.success) {
          throw new Error(response.data.error || 'API Error');
        }
        return response.data.data;
      };
      
      mockTaskService.getTaskStatus.mockResolvedValue({
        id: 1,
        status: 'completed',
        progress: 100
      });
      
      const response = await request(app).get('/api/tasks/1');
      
      const modernData = modernParseResponse(response);
      expect(modernData).toHaveProperty('id', 1);
      expect(modernData).toHaveProperty('status', 'completed');
      
      console.log('✅ MIGRATION: Modern frontend parsing works correctly');
    });
  });
});

/**
 * API Standardization Testing Strategy - План Валидации
 * 
 * 📋 ПЛАН ВАЛИДАЦИИ ИСПРАВЛЕНИЙ:
 * 
 * 1. PRE-STANDARDIZATION VALIDATION:
 *    - ✅ Определение стандартного формата { success, data, error }
 *    - ✅ Валидация текущих несогласованностей
 *    - ✅ Проверка backward compatibility
 * 
 * 2. POST-STANDARDIZATION VALIDATION:
 *    - ⏳ Все endpoints возвращают стандартный формат
 *    - ⏳ Ошибки обрабатываются единообразно
 *    - ⏳ Frontend код обновлен для работы с новым форматом
 *    - ⏳ Performance не деградировал
 * 
 * 3. IMPLEMENTATION STRATEGY:
 *    - Мидлваре для автоматического обертывания
 *    - Type definitions для TypeScript
 *    - Обновление всех controllers
 *    - Обновление frontend API клиента
 * 
 * 🎯 КРИТЕРИИ УСПЕХА:
 * - 100% endpoints соответствуют стандарту
 * - Frontend код упрощается (убираем response.data.data || response.data)
 * - Ошибки обрабатываются единообразно
 * - Backward compatibility сохраняется для плавной миграции
 * - API documentation обновляется
 * 
 * 📊 МЕТРИКИ ВАЛИДАЦИИ:
 * - Response time consistency: все endpoints < 500ms
 * - Error handling coverage: 100% error scenarios
 * - Frontend compatibility: 0 breaking changes
 * - Documentation completeness: 100% endpoints documented
 * - Type safety: 100% TypeScript coverage
 */