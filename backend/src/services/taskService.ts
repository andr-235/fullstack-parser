import logger from '@/utils/logger';
import { DatabaseRepository } from '@/repositories/dbRepo';
import { Task } from '@/models/task';
import {
  TaskAttributes,
  TaskCreationAttributes,
  TaskStatus,
  TaskType,
  TaskResponse,
  CreateTaskRequest
} from '@/types/task';

interface ListTasksOptions {
  limit: number;
  offset: number;
  status?: TaskStatus;
  type?: TaskType;
}

interface ListTasksResult {
  tasks: Task[];
  total: number;
}

interface TaskMetrics {
  posts: number;
  comments: number;
  errors: string[];
}

interface TaskStatusResponse {
  status: TaskStatus;
  type: TaskType;
  priority: number;
  progress: number;
  metrics: TaskMetrics;
  errors: string[];
  groups: any[];
  parameters: Record<string, any>;
  result: any;
  error: string | null;
  executionTime: number | null;
  startedAt: Date | null;
  finishedAt: Date | null;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

interface CreateTaskResponse {
  taskId: number;
  status: TaskStatus;
}

interface StartCollectResponse {
  status: TaskStatus;
  startedAt: Date | null;
}

class TaskService {
  private dbRepo: DatabaseRepository;

  constructor(dbRepoInstance?: DatabaseRepository) {
    this.dbRepo = dbRepoInstance || new DatabaseRepository();
  }

  async createTask(taskData: CreateTaskRequest): Promise<CreateTaskResponse> {
    try {
      // Создаем задачу с новой структурой данных
      const taskCreationData: Partial<TaskAttributes> = {
        type: taskData.type || 'fetch_comments',
        priority: 0, // Будет установлен в модели по умолчанию
        groups: taskData.groupIds || [],
        parameters: taskData.options || {},
        metadata: {
          ...taskData.options,
          groupIds: taskData.groupIds,
          postUrls: taskData.postUrls
        },
        status: 'pending' // Начальный статус
      };

      const task = await this.dbRepo.createTask(taskCreationData);
      return { taskId: task.id, status: task.status };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to create task', { error: errorMsg });
      throw new Error(`Failed to create task: ${errorMsg}`);
    }
  }

  async getTaskById(taskId: number): Promise<Task | null> {
    try {
      return await this.dbRepo.getTaskById(taskId);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get task by ID', { taskId, error: errorMsg });
      throw new Error(`Failed to get task: ${errorMsg}`);
    }
  }

  async startCollect(taskId: number): Promise<StartCollectResponse> {
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
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to start collect', { taskId, error: errorMsg });
      throw new Error(`Failed to start collect: ${errorMsg}`);
    }
  }

  async getTaskStatus(taskId: number): Promise<TaskStatusResponse> {
    try {
      const task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        throw new Error('Task not found');
      }

      // Безопасно извлекаем метрики из metadata
      const metadata = task.metadata || {};
      const metrics: TaskMetrics = {
        posts: metadata.posts || 0,
        comments: metadata.comments || 0,
        errors: metadata.errors || []
      };

      return {
        status: task.status,
        type: task.type,
        priority: task.priority,
        progress: task.progress,
        metrics,
        errors: metrics.errors,
        groups: task.groups || [],
        parameters: task.parameters || {},
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
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get task status', { taskId, error: errorMsg });
      throw new Error(`Failed to get task status: ${errorMsg}`);
    }
  }

  /**
   * Получает список задач с пагинацией и фильтрами.
   */
  async listTasks(
    page = 1,
    limit = 10,
    status?: TaskStatus,
    type?: TaskType
  ): Promise<ListTasksResult> {
    try {
      const offset = (page - 1) * limit;
      const options: ListTasksOptions = {
        limit,
        offset,
        status,
        type
      };

      const result = await this.dbRepo.listTasks(options);
      return result;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to list tasks', { page, limit, status, type, error: errorMsg });
      throw new Error(`Failed to list tasks: ${errorMsg}`);
    }
  }

  /**
   * Обновляет прогресс выполнения задачи
   */
  async updateTaskProgress(taskId: number, progress: number, metadata?: Record<string, any>): Promise<void> {
    try {
      const task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        throw new Error('Task not found');
      }

      task.progress = Math.min(100, Math.max(0, progress));

      if (metadata) {
        task.metadata = { ...task.metadata, ...metadata };
      }

      await task.save();

      logger.info('Task progress updated', { taskId, progress, metadata });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to update task progress', { taskId, progress, error: errorMsg });
      throw new Error(`Failed to update task progress: ${errorMsg}`);
    }
  }

  /**
   * Помечает задачу как завершенную
   */
  async completeTask(taskId: number, result?: any): Promise<void> {
    try {
      const task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        throw new Error('Task not found');
      }

      await task.markAsCompleted(result);
      logger.info('Task completed', { taskId });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to complete task', { taskId, error: errorMsg });
      throw new Error(`Failed to complete task: ${errorMsg}`);
    }
  }

  /**
   * Помечает задачу как провалившуюся
   */
  async failTask(taskId: number, errorMessage: string): Promise<void> {
    try {
      const task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        throw new Error('Task not found');
      }

      await task.markAsFailed(errorMessage);
      logger.error('Task failed', { taskId, error: errorMessage });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to fail task', { taskId, error: errorMsg });
      throw new Error(`Failed to fail task: ${errorMsg}`);
    }
  }

  /**
   * Получает статистику по задачам
   */
  async getTaskStats(): Promise<Record<TaskStatus, number>> {
    try {
      return await this.dbRepo.getTaskStats();
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get task stats', { error: errorMsg });
      throw new Error(`Failed to get task stats: ${errorMsg}`);
    }
  }
}

const taskService = new TaskService();
export default taskService;
export { TaskService };
export type {
  ListTasksOptions,
  ListTasksResult,
  TaskMetrics,
  TaskStatusResponse,
  CreateTaskResponse,
  StartCollectResponse
};