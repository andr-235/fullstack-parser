const logger = require('../utils/logger');
const dbRepo = require('../repositories/dbRepo');

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

      const { queue } = await import('../../config/queue.js');
      await queue.add('collect', { taskId }, { delay: 0 });

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
      return {
        status: task.status,
        progress: task.metrics || { posts: 0, comments: 0 },
        errors: task.metrics?.errors || [],
        groups: task.groups
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

const taskServiceInstance = new TaskService();

module.exports = taskServiceInstance;
module.exports.createTask = taskServiceInstance.createTask.bind(taskServiceInstance);
module.exports.getTaskStatus = taskServiceInstance.getTaskStatus.bind(taskServiceInstance);
module.exports.startCollect = taskServiceInstance.startCollect.bind(taskServiceInstance);
module.exports.listTasks = taskServiceInstance.listTasks.bind(taskServiceInstance);