// Mock всех зависимостей
jest.mock('../../src/repositories/vkApi', () => {
  const mocked = {
    getPosts: jest.fn(),
    getComments: jest.fn()
  };
  return {
    __esModule: false,
    default: mocked,
    ...mocked
  };
});

jest.mock('../../src/config/queue', () => ({
  __esModule: false,
  default: {
    queue: {
      add: jest.fn()
    }
  },
  queue: {
    add: jest.fn()
  }
}));

jest.mock('axios-retry', () => {
  const retry = jest.fn();
  retry.exponentialDelay = jest.fn();

  return {
    __esModule: false,
    default: retry,
    exponentialDelay: retry.exponentialDelay
  };
});

jest.mock('axios', () => {
  const axiosInstance = {
    get: jest.fn(),
    interceptors: {
      request: { use: jest.fn((fn) => fn({})) },
      response: { use: jest.fn((fn) => fn({})) }
    }
  };

  const axios = {
    create: jest.fn(() => axiosInstance)
  };

  return {
    __esModule: false,
    default: axios,
    ...axios,
    __INSTANCE__: axiosInstance
  };
});

jest.mock('../../src/services/taskService', () => {
  const service = {
    createTask: jest.fn(async () => ({ taskId: 1, status: 'created' })),
    getTaskStatus: jest.fn(async () => ({ status: 'completed', progress: { posts: 1, comments: 0 }, errors: [] })),
    startCollect: jest.fn(async () => ({ status: 'pending' })),
    listTasks: jest.fn(async () => ({ tasks: [], total: 0 }))
  };
  return {
    __esModule: false,
    default: service,
    ...service
  };
});

const mockTaskService = require('../../src/services/taskService');

jest.mock('../../src/repositories/dbRepo', () => ({
  __esModule: false,
  default: {
    createTask: jest.fn(),
    getTaskById: jest.fn(),
    updateTask: jest.fn(),
    listTasks: jest.fn()
  },
  createTask: jest.fn(),
  getTaskById: jest.fn(),
  updateTask: jest.fn(),
  listTasks: jest.fn()
}));

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
const server = app.default || app;

describe('API Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/groups', () => {
    it('should create a task for group and return 201 with taskId', async () => {
      const mockTask = { taskId: 1 };
      mockTaskService.createTask.mockResolvedValue(mockTask);

      const response = await request(server)
        .post('/api/groups')
        .send({ groups: [123] })
        .expect(201);

      expect(response.body).toEqual({ taskId: 1, status: 'created' });
      expect(mockTaskService.createTask).toHaveBeenCalledWith([123]);
    });
  });

  describe('POST /api/collect/:taskId', () => {
    it('should start collection and return 202', async () => {
      mockTaskService.startCollect.mockResolvedValue({ status: 'pending', startedAt: '2025-01-01T00:00:00.000Z' });

      const response = await request(server)
        .post('/api/collect/1')
        .expect(202);

      expect(response.body).toMatchObject({ status: 'pending' });
      expect(mockTaskService.startCollect).toHaveBeenCalledWith(1);
    });
  });

  describe('GET /api/tasks/:taskId', () => {
    it('should get task status and return 200', async () => {
      const mockStatus = { status: 'completed', progress: { posts: 1, comments: 2 }, errors: [] };
      mockTaskService.getTaskStatus.mockResolvedValue(mockStatus);

      const response = await request(server)
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

      const response = await request(server)
        .get('/api/tasks')
        .expect(200);

      expect(response.body).toEqual(mockList);
      expect(mockTaskService.listTasks).toHaveBeenCalledWith(1, 10);
    });
  });

  describe('Error handling', () => {
    it('should return 500 on service error', async () => {
      mockTaskService.createTask.mockRejectedValue(new Error('Service error'));

      const response = await request(server)
        .post('/api/groups')
        .send({ groups: [123] })
        .expect(500);

      expect(response.body.error).toBeDefined();
    });
  });
});