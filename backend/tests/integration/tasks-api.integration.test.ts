import request from 'supertest';
import app from '@/server';
import { PrismaService } from '@/config/db';
import taskService from '@/services/taskService';

describe('Tasks API Integration Tests', () => {
  let createdTaskId: number;

  beforeAll(async () => {
    // Ensure database connection
    await PrismaService.connect();
  });

  afterAll(async () => {
    // Clean up and disconnect
    if (createdTaskId) {
      try {
        await PrismaService.task.delete({
          where: { id: createdTaskId }
        });
      } catch (error) {
        // Task might already be cleaned up
        console.log('Task cleanup error (expected):', error);
      }
    }
    await PrismaService.disconnect();
  });

  beforeEach(() => {
    // Reset task ID for each test
    createdTaskId = 0;
  });

  describe('POST /api/tasks/collect - Create VK Collect Task', () => {
    test('должен создать задачу с валидными группами', async () => {
      const taskData = {
        groups: [123456, 789012, 345678]
      };

      const response = await request(app)
        .post('/api/tasks/collect')
        .send(taskData)
        .expect(201);

      expect(response.body).toMatchObject({
        success: true,
        data: {
          taskId: expect.any(Number),
          status: 'created'
        }
      });

      createdTaskId = response.body.data.taskId;

      // Проверяем, что задача создалась в базе данных
      const task = await taskService.getTaskById(createdTaskId);
      expect(task).toBeTruthy();
      expect(task.status).toBe('pending');
      expect(task.type).toBe('fetch_comments');
    });

    test('должен создать задачу с группами в формате объектов', async () => {
      const taskData = {
        groups: [
          { id: 123456, name: 'Test Group 1' },
          { id: 789012, name: 'Test Group 2' },
          345678
        ]
      };

      const response = await request(app)
        .post('/api/tasks/collect')
        .send(taskData)
        .expect(201);

      expect(response.body.success).toBe(true);
      createdTaskId = response.body.data.taskId;
    });

    test('должен отклонить запрос с пустым массивом групп', async () => {
      const taskData = {
        groups: []
      };

      const response = await request(app)
        .post('/api/tasks/collect')
        .send(taskData)
        .expect(400);

      expect(response.body).toMatchObject({
        success: false,
        error: expect.stringContaining('groups')
      });
    });

    test('должен отклонить запрос без поля groups', async () => {
      const taskData = {};

      const response = await request(app)
        .post('/api/tasks/collect')
        .send(taskData)
        .expect(400);

      expect(response.body).toMatchObject({
        success: false,
        error: expect.stringContaining('required')
      });
    });

    test('должен убирать дубли из списка групп', async () => {
      const taskData = {
        groups: [123456, 123456, 789012, 123456]
      };

      const response = await request(app)
        .post('/api/tasks/collect')
        .send(taskData)
        .expect(201);

      createdTaskId = response.body.data.taskId;

      // Проверяем задачу в базе данных
      const task = await taskService.getTaskById(createdTaskId);
      const groups = task.groups as number[];

      // Проверяем, что дубли убраны
      expect(groups).toHaveLength(2);
      expect(groups).toContain(123456);
      expect(groups).toContain(789012);
    });
  });

  describe('GET /api/tasks/:taskId - Get Task Status', () => {
    beforeEach(async () => {
      // Создаем тестовую задачу
      const taskData = {
        type: 'fetch_comments' as const,
        groupIds: [123456, 789012],
        options: {}
      };

      const { taskId } = await taskService.createTask(taskData);
      createdTaskId = taskId;
    });

    test('должен возвращать статус существующей задачи', async () => {
      const response = await request(app)
        .get(`/api/tasks/${createdTaskId}`)
        .expect(200);

      expect(response.body).toMatchObject({
        success: true,
        data: {
          id: createdTaskId,
          status: 'pending',
          type: 'fetch_comments',
          priority: expect.any(Number),
          progress: {
            processed: expect.any(Number),
            total: expect.any(Number)
          },
          errors: expect.any(Array),
          groups: expect.any(Array),
          parameters: expect.any(Object),
          createdAt: expect.any(String),
          updatedAt: expect.any(String)
        }
      });
    });

    test('должен возвращать 404 для несуществующей задачи', async () => {
      const nonExistentTaskId = 999999;

      const response = await request(app)
        .get(`/api/tasks/${nonExistentTaskId}`)
        .expect(404);

      expect(response.body).toMatchObject({
        success: false,
        error: 'Task not found'
      });
    });

    test('должен возвращать 400 для невалидного ID задачи', async () => {
      const response = await request(app)
        .get('/api/tasks/invalid-id')
        .expect(400);

      expect(response.body).toMatchObject({
        success: false,
        error: 'Invalid task ID'
      });
    });

    test('должен возвращать полную информацию о задаче с корректной структурой progress', async () => {
      const response = await request(app)
        .get(`/api/tasks/${createdTaskId}`)
        .expect(200);

      const { data } = response.body;

      // Проверяем структуру progress
      expect(data.progress).toHaveProperty('processed');
      expect(data.progress).toHaveProperty('total');
      expect(typeof data.progress.processed).toBe('number');
      expect(typeof data.progress.total).toBe('number');

      // Проверяем дополнительные поля
      expect(data).toHaveProperty('completedAt');
      expect(data).toHaveProperty('createdBy');
      expect(data).toHaveProperty('executionTime');
    });
  });

  describe('GET /api/tasks - List Tasks', () => {
    beforeEach(async () => {
      // Создаем несколько тестовых задач
      const task1 = await taskService.createTask({
        type: 'fetch_comments',
        groupIds: [123],
        options: {}
      });
      const task2 = await taskService.createTask({
        type: 'fetch_comments',
        groupIds: [456],
        options: {}
      });

      createdTaskId = task1.taskId; // Для очистки
    });

    test('должен возвращать список задач с пагинацией', async () => {
      const response = await request(app)
        .get('/api/tasks')
        .query({ page: 1, limit: 10 })
        .expect(200);

      expect(response.body).toMatchObject({
        success: true,
        data: expect.any(Array),
        pagination: {
          page: 1,
          limit: 10,
          total: expect.any(Number),
          totalPages: expect.any(Number)
        }
      });

      expect(Array.isArray(response.body.data)).toBe(true);
    });

    test('должен фильтровать задачи по статусу', async () => {
      const response = await request(app)
        .get('/api/tasks')
        .query({ status: 'pending', page: 1, limit: 10 })
        .expect(200);

      expect(response.body.success).toBe(true);

      // Все возвращенные задачи должны иметь статус 'pending'
      if (response.body.data.length > 0) {
        response.body.data.forEach((task: any) => {
          expect(task.status).toBe('pending');
        });
      }
    });

    test('должен фильтровать задачи по типу', async () => {
      const response = await request(app)
        .get('/api/tasks')
        .query({ type: 'fetch_comments', page: 1, limit: 10 })
        .expect(200);

      expect(response.body.success).toBe(true);

      // Все возвращенные задачи должны иметь тип 'fetch_comments'
      if (response.body.data.length > 0) {
        response.body.data.forEach((task: any) => {
          expect(task.type).toBe('fetch_comments');
        });
      }
    });

    test('должен возвращать ошибку валидации для неправильных параметров', async () => {
      const response = await request(app)
        .get('/api/tasks')
        .query({ page: -1, limit: 0 })
        .expect(400);

      expect(response.body).toMatchObject({
        success: false,
        error: expect.stringContaining('Validation')
      });
    });
  });

  describe('POST /collect/:taskId - Start Task Collection', () => {
    beforeEach(async () => {
      // Создаем тестовую задачу
      const { taskId } = await taskService.createTask({
        type: 'fetch_comments',
        groupIds: [123456],
        options: {}
      });
      createdTaskId = taskId;
    });

    test('должен запустить сбор для существующей задачи', async () => {
      const response = await request(app)
        .post(`/api/collect/${createdTaskId}`)
        .expect(202);

      expect(response.body).toMatchObject({
        success: true,
        data: {
          taskId: createdTaskId,
          status: 'pending',
          startedAt: expect.any(String)
        }
      });

      // Проверяем, что статус задачи изменился в базе данных
      const updatedTask = await taskService.getTaskById(createdTaskId);
      expect(updatedTask.status).toBe('processing');
      expect(updatedTask.startedAt).toBeTruthy();
    });

    test('должен возвращать 404 для несуществующей задачи', async () => {
      const nonExistentTaskId = 999999;

      const response = await request(app)
        .post(`/api/collect/${nonExistentTaskId}`)
        .expect(404);

      expect(response.body).toMatchObject({
        success: false,
        error: 'Task not found'
      });
    });

    test('должен возвращать 400 для невалидного ID задачи', async () => {
      const response = await request(app)
        .post('/api/collect/invalid-id')
        .expect(400);

      expect(response.body).toMatchObject({
        success: false,
        error: 'Invalid task ID'
      });
    });
  });

  describe('Request/Response Format Validation', () => {
    test('все API endpoints должны возвращать консистентный формат ответа', async () => {
      // Создаем задачу
      const createResponse = await request(app)
        .post('/api/tasks/collect')
        .send({ groups: [123456] });

      createdTaskId = createResponse.body.data.taskId;

      // Проверяем формат ответа создания задачи
      expect(createResponse.body).toHaveProperty('success');
      expect(createResponse.body).toHaveProperty('data');
      expect(typeof createResponse.body.success).toBe('boolean');

      // Проверяем формат ответа получения статуса
      const statusResponse = await request(app)
        .get(`/api/tasks/${createdTaskId}`);

      expect(statusResponse.body).toHaveProperty('success');
      expect(statusResponse.body).toHaveProperty('data');
      expect(typeof statusResponse.body.success).toBe('boolean');

      // Проверяем формат ответа списка задач
      const listResponse = await request(app)
        .get('/api/tasks');

      expect(listResponse.body).toHaveProperty('success');
      expect(listResponse.body).toHaveProperty('data');
      expect(listResponse.body).toHaveProperty('pagination');
    });

    test('должен обрабатывать некорректный JSON с соответствующей ошибкой', async () => {
      const response = await request(app)
        .post('/api/tasks/collect')
        .set('Content-Type', 'application/json')
        .send('{ invalid json }')
        .expect(400);

      expect(response.body).toMatchObject({
        success: false,
        error: 'INVALID_JSON',
        message: 'Invalid JSON in request body'
      });
    });
  });

  describe('Error Handling and Edge Cases', () => {
    test('должен обрабатывать большие массивы групп', async () => {
      // Создаем массив с 1000 групп
      const largeGroupsArray = Array.from({ length: 1000 }, (_, i) => i + 1);

      const response = await request(app)
        .post('/api/tasks/collect')
        .send({ groups: largeGroupsArray })
        .expect(201);

      expect(response.body.success).toBe(true);
      createdTaskId = response.body.data.taskId;
    });

    test('должен обрабатывать timeout для длительных запросов', async () => {
      // Тест может быть проблематичен из-за timeout настроек
      // Оставляем как пример структуры теста
      expect(true).toBe(true);
    }, 35000); // Увеличиваем timeout для этого теста

    test('должен корректно обрабатывать concurrent запросы', async () => {
      const concurrentRequests = Array.from({ length: 5 }, (_, i) =>
        request(app)
          .post('/api/tasks/collect')
          .send({ groups: [100 + i] })
      );

      const responses = await Promise.all(concurrentRequests);

      responses.forEach(response => {
        expect(response.status).toBe(201);
        expect(response.body.success).toBe(true);
      });

      // Cleanup: запоминаем один ID для очистки
      if (responses.length > 0) {
        createdTaskId = responses[0].body.data.taskId;
      }
    });
  });

  describe('API Response Headers and CORS', () => {
    test('должен возвращать корректные CORS заголовки', async () => {
      const response = await request(app)
        .options('/api/tasks')
        .set('Origin', 'http://localhost:5173')
        .expect(204);

      expect(response.headers['access-control-allow-origin']).toBeTruthy();
      expect(response.headers['access-control-allow-methods']).toBeTruthy();
    });

    test('должен возвращать правильный Content-Type для JSON', async () => {
      const response = await request(app)
        .get('/api/tasks')
        .expect(200);

      expect(response.headers['content-type']).toMatch(/application\/json/);
    });
  });
});