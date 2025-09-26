const logger = require('../utils/logger.js');

const dbRepo = require('../repositories/dbRepo.js');

class TaskService {
  constructor(dbRepoInstance) {
    this.dbRepo = dbRepoInstance || dbRepo;
  }

  async createTask(taskData) {
    try {
      // Создаем задачу с новой структурой данных
      const task = await this.dbRepo.createTask({
        type: taskData.type || 'fetch_comments',
        priority: taskData.priority || 0,
        groups: taskData.groups,
        parameters: taskData.parameters || {},
        metrics: taskData.metrics || { posts: 0, comments: 0, errors: [] },
        createdBy: taskData.createdBy || 'system',
        status: 'pending' // Начальный статус согласно новой модели
      });
      return { taskId: task.id, status: task.status };
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
      if (task.status !== 'pending') {
        throw new Error('Task is not in pending status');
      }

      // Используем новый метод модели Task для установки статуса processing
      await task.markAsProcessing();

      // Note: Background collection is now handled by BullMQ queue
      // This method is for manual task starts if needed

      return { status: 'processing', startedAt: task.startedAt };
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
      const metrics = task.metrics || { posts: 0, comments: 0, errors: [] };
      return {
        status: task.status,
        type: task.type,
        priority: task.priority,
        progress: task.progress, // Используем dedicated поле progress
        metrics: metrics,
        errors: metrics?.errors || [],
        groups: task.groups || [],
        parameters: task.parameters,
        result: task.result,
        error: task.error,
        executionTime: task.executionTime,
        startedAt: task.startedAt,
        finishedAt: task.finishedAt,
        createdBy: task.createdBy,
        createdAt: task.createdAt,
        updatedAt: task.updatedAt
      };
    } catch (error) {
      logger.error('Failed to get task status', { taskId, error: error.message });
      throw new Error(`Failed to get task status: ${error.message}`);
    }
  }

  /**
   * Получает список задач с пагинацией и фильтрами.
   * @param {number} page - Номер страницы
   * @param {number} limit - Количество задач на странице
   * @param {string} [status] - Фильтр по статусу (pending, processing, completed, failed)
   * @param {string} [type] - Фильтр по типу (fetch_comments, process_groups, analyze_posts)
   * @returns {Promise<{tasks: Array, total: number}>} Список задач и общее количество
   */
  async listTasks(page = 1, limit = 10, status, type) {
    try {
      const offset = (page - 1) * limit;
      const { tasks, total } = await this.dbRepo.listTasks({
        limit,
        offset,
        status,
        type
      });
      return { tasks, total };
    } catch (error) {
      logger.error('Failed to list tasks', { page, limit, status, type, error: error.message });
      throw new Error(`Failed to list tasks: ${error.message}`);
    }
  }
}

module.exports = new TaskService();