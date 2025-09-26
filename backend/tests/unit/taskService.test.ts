import { createTask, getTaskStatus, startCollect, listTasks } from '../../src/services/taskService';
import dbRepo from '../../src/repositories/dbRepo';

jest.mock('../../src/repositories/dbRepo');

describe('TaskService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createTask', () => {
    it('should create a task and return taskId and status', async () => {
      const mockTask = { id: 1, status: 'created' };
      dbRepo.createTask.mockResolvedValue(mockTask);

      const result = await createTask(123);

      expect(dbRepo.createTask).toHaveBeenCalledWith(123);
      expect(result).toEqual({ taskId: 1, status: 'created' });
    });

    it('should handle error when creating task', async () => {
      dbRepo.createTask.mockRejectedValue(new Error('DB error'));

      await expect(createTask(123)).rejects.toThrow('DB error');
    });
  });

  describe('getTaskStatus', () => {
    it('should get task status and progress', async () => {
      const mockStatus = { status: 'pending', progress: 50 };
      dbRepo.getTaskById.mockResolvedValue(mockStatus);

      const result = await getTaskStatus(1);

      expect(dbRepo.getTaskById).toHaveBeenCalledWith(1);
      expect(result).toEqual({ status: 'pending', progress: 50 });
    });
  });

  describe('startCollect', () => {
    it('should add task to queue and return pending status', async () => {
      const mockQueue = { add: jest.fn().mockResolvedValue('task-added') };
      // Assume queue is mocked or imported
      const result = await startCollect(1);

      expect(mockQueue.add).toHaveBeenCalledWith('collect', { taskId: 1 });
      expect(result).toEqual({ status: 'pending' });
    });
  });

  describe('listTasks', () => {
    it('should list tasks and return tasks and total count', async () => {
      const mockTasks = [{ id: 1, status: 'completed' }];
      const mockTotal = 1;
      dbRepo.findAndCountAll.mockResolvedValue({ rows: mockTasks, count: mockTotal });

      const result = await listTasks();

      expect(dbRepo.findAndCountAll).toHaveBeenCalled();
      expect(result).toEqual({ tasks: mockTasks, total: 1 });
    });
  });
});