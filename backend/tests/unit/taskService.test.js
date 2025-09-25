// Mock dbRepo перед импортом
const mockDbRepo = {
  createTask: jest.fn(),
  getTaskById: jest.fn(),
  updateTaskStatus: jest.fn(),
  saveResults: jest.fn(),
  getTaskResults: jest.fn(),
  getTasks: jest.fn()
};

jest.mock('../../src/repositories/dbRepo', () => mockDbRepo);

const { createTask, getTaskStatus, startCollect, listTasks } = require('../../src/services/taskService');

describe('TaskService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createTask', () => {
    it('should create a task and return taskId and status', async () => {
      const mockTask = { id: 'test-uuid', status: 'created' };
      mockDbRepo.createTask.mockResolvedValue(mockTask);

      const result = await createTask(['test'], 'test-group');

      expect(result).toEqual({
        taskId: 'test-uuid',
        status: 'created'
      });
      expect(mockDbRepo.createTask).toHaveBeenCalledWith(['test'], 'test-group');
    });

    it('should throw error when dbRepo fails', async () => {
      const errorMessage = 'Database error';
      mockDbRepo.createTask.mockRejectedValue(new Error(errorMessage));

      await expect(createTask(['test'], 'test-group')).rejects.toThrow(`Failed to create task: ${errorMessage}`);
    });
  });

  describe('getTaskStatus', () => {
    it('should get task status and return status with progress', async () => {
      const mockTask = { id: 'test-uuid', status: 'completed', progress: 100 };
      mockDbRepo.getTaskById.mockResolvedValue(mockTask);

      const result = await getTaskStatus('test-uuid');

      expect(result).toEqual({
        status: 'completed',
        progress: 100
      });
      expect(mockDbRepo.getTaskById).toHaveBeenCalledWith('test-uuid');
    });

    it('should throw error when task not found', async () => {
      mockDbRepo.getTaskById.mockResolvedValue(null);

      await expect(getTaskStatus('non-existent')).rejects.toThrow('Task not found');
    });
  });

  describe('listTasks', () => {
    it('should list tasks with pagination', async () => {
      const mockTasks = {
        tasks: [{ id: '1', status: 'completed' }],
        total: 1
      };
      mockDbRepo.getTasks.mockResolvedValue(mockTasks);

      const result = await listTasks(1, 10);

      expect(result).toEqual(mockTasks);
      expect(mockDbRepo.getTasks).toHaveBeenCalledWith(1, 10);
    });
  });
});