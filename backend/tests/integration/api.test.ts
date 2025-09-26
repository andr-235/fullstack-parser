import request from 'supertest';
import app from '../../server';
import * as taskService from '../../src/services/taskService';

jest.mock('../../src/services/taskService');

describe('API Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/groups', () => {
    it('should create a task for group and return 201 with taskId', async () => {
      const mockTask = { taskId: 1 };
      taskService.createTask.mockResolvedValue(mockTask);

      const response = await request(app)
        .post('/api/groups')
        .send({ groupId: 123 })
        .expect(201);

      expect(response.body).toEqual({ taskId: 1 });
      expect(taskService.createTask).toHaveBeenCalledWith(123);
    });
  });

  describe('POST /api/collect/:taskId', () => {
    it('should start collection and return 202', async () => {
      taskService.startCollect.mockResolvedValue({ status: 'pending' });

      const response = await request(app)
        .post('/api/collect/1')
        .expect(202);

      expect(response.body).toEqual({ status: 'pending' });
      expect(taskService.startCollect).toHaveBeenCalledWith(1);
    });
  });

  describe('GET /api/tasks/:taskId', () => {
    it('should get task status and return 200', async () => {
      const mockStatus = { status: 'completed', progress: 100 };
      taskService.getTaskStatus.mockResolvedValue(mockStatus);

      const response = await request(app)
        .get('/api/tasks/1')
        .expect(200);

      expect(response.body).toEqual(mockStatus);
      expect(taskService.getTaskStatus).toHaveBeenCalledWith(1);
    });
  });

  describe('GET /api/tasks', () => {
    it('should list tasks and return 200', async () => {
      const mockList = { tasks: [], total: 0 };
      taskService.listTasks.mockResolvedValue(mockList);

      const response = await request(app)
        .get('/api/tasks')
        .expect(200);

      expect(response.body).toEqual(mockList);
      expect(taskService.listTasks).toHaveBeenCalled();
    });
  });

  describe('Error handling', () => {
    it('should return 500 on service error', async () => {
      taskService.createTask.mockRejectedValue(new Error('Service error'));

      const response = await request(app)
        .post('/api/groups')
        .send({ groupId: 123 })
        .expect(500);

      expect(response.body.error).toBeDefined();
    });
  });
});