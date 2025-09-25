// Mock всех зависимостей
jest.mock('../../src/repositories/vkApi', () => ({
  getPosts: jest.fn(),
  getComments: jest.fn()
}));

jest.mock('../../src/config/queue', () => ({
  queue: {
    add: jest.fn()
  }
}));

jest.mock('axios-retry', () => ({
  __esModule: true,
  default: jest.fn(),
  exponentialDelay: jest.fn()
}));

jest.mock('axios', () => ({
  default: {
    get: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  }
}));

const mockTaskService = {
  createTask: jest.fn(),
  getTaskStatus: jest.fn(),
  startCollect: jest.fn(),
  listTasks: jest.fn()
};

jest.mock('../../src/services/taskService', () => mockTaskService);

const request = require('supertest');

// Мок базы данных перед импортом server.js
jest.mock('../../src/config/db', () => ({
  sequelize: {
    authenticate: jest.fn().mockResolvedValue(),
    close: jest.fn().mockResolvedValue()
  },
  Task: {},
  Post: {},
  Comment: {}
}));

const app = require('../../server.js');

describe('API Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/groups', () => {
    it('should create a task for group and return 201 with taskId', async () => {
      const mockTask = { taskId: 1 };
      mockTaskService.createTask.mockResolvedValue(mockTask);

      const response = await request(app)
        .post('/api/groups')
        .send({ groupId: 123 })
        .expect(201);

      expect(response.body).toEqual({ taskId: 1 });
      expect(mockTaskService.createTask).toHaveBeenCalledWith(123);
    });
  });

  describe('POST /api/collect/:taskId', () => {
    it('should start collection and return 202', async () => {
      mockTaskService.startCollect.mockResolvedValue({ status: 'pending' });

      const response = await request(app)
        .post('/api/collect/1')
        .expect(202);

      expect(response.body).toEqual({ status: 'pending' });
      expect(mockTaskService.startCollect).toHaveBeenCalledWith(1);
    });
  });

  describe('GET /api/tasks/:taskId', () => {
    it('should get task status and return 200', async () => {
      const mockStatus = { status: 'completed', progress: 100 };
      mockTaskService.getTaskStatus.mockResolvedValue(mockStatus);

      const response = await request(app)
        .get('/api/tasks/1')
        .expect(200);

      expect(response.body).toEqual(mockStatus);
      expect(mockTaskService.getTaskStatus).toHaveBeenCalledWith(1);
    });
  });

  describe('GET /api/tasks', () => {
    it('should list tasks and return 200', async () => {
      const mockList = { tasks: [], total: 0 };
      mockTaskService.listTasks.mockResolvedValue(mockList);

      const response = await request(app)
        .get('/api/tasks')
        .expect(200);

      expect(response.body).toEqual(mockList);
      expect(mockTaskService.listTasks).toHaveBeenCalled();
    });
  });

  describe('Error handling', () => {
    it('should return 500 on service error', async () => {
      mockTaskService.createTask.mockRejectedValue(new Error('Service error'));

      const response = await request(app)
        .post('/api/groups')
        .send({ groupId: 123 })
        .expect(500);

      expect(response.body.error).toBeDefined();
    });
  });
});