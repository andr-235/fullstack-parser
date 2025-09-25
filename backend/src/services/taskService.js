const logger = require('../utils/logger.js');

const dbRepo = require('../repositories/dbRepo.js');

class TaskService {
  constructor(dbRepoInstance) {
    this.dbRepo = dbRepoInstance || dbRepo;
  }

  async createTask(groups) {
    try {
      const task = await this.dbRepo.createTask({
        groups,
        status: 'created',
        metrics: { posts: 0, comments: 0, errors: [] }
      });
      return { taskId: task.id, status: 'created' };
    } catch (error) {
      logger.error('Failed to create task', { error: error.message });
      throw new Error(`Failed to create task: ${error.message}`);
    }
  }

  async getTaskById(taskId) {
    return await this.dbRepo.getTaskById(taskId);
  }

  async startCollect(taskId) {
    try {
      const task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        throw new Error('Task not found');
      }
      if (task.status !== 'created') {
        throw new Error('Task is not in created status');
      }

      await this.dbRepo.updateTask(taskId, {
        status: 'in_progress',
        startedAt: new Date()
      });

      // Note: Background collection is now handled by BullMQ queue
      // This method is for manual task starts if needed

      return { status: 'pending', startedAt: new Date() };
    } catch (error) {
      logger.error('Failed to start collect', { taskId, error: error.message });
      throw new Error(`Failed to start collect: ${error.message}`);
    }
  }

  async getTaskStatus(taskId) {
    try {
      const task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        throw new Error('Task not found');
      }
      const metrics = task.metrics ? JSON.parse(task.metrics) : { posts: 0, comments: 0, errors: [] };
      return {
        status: task.status,
        progress: metrics || { posts: 0, comments: 0 },
        errors: metrics?.errors || [],
        groups: JSON.parse(task.groups || '[]')
      };
    } catch (error) {
      logger.error('Failed to get task status', { taskId, error: error.message });
      throw new Error(`Failed to get task status: ${error.message}`);
    }
  }

  async listTasks(page = 1, limit = 10) {
    try {
      const offset = (page - 1) * limit;
      const { tasks, total } = await this.dbRepo.listTasks({ limit, offset });
      return { tasks, total };
    } catch (error) {
      logger.error('Failed to list tasks', { page, limit, error: error.message });
      throw new Error(`Failed to list tasks: ${error.message}`);
    }
  }
}

module.exports = new TaskService();