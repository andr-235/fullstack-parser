import logger from '@/utils/logger';
import dbRepo, { DBRepo } from '@/repositories/dbRepo';
import type { Prisma } from '@prisma/client';
import {
  CreateTaskRequest
} from '@/types/task';

interface ListTasksOptions {
  limit: number;
  offset: number;
  status?: "pending" | "processing" | "completed" | "failed";
  type?: "fetch_comments" | "process_groups" | "analyze_posts";
}

interface ListTasksResult {
  tasks: any[];
  total: number;
}

interface TaskMetrics {
  posts: number;
  comments: number;
  errors: string[];
}

interface TaskStatusResponse {
  status: "pending" | "processing" | "completed" | "failed";
  type: "fetch_comments" | "process_groups" | "analyze_posts";
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
  status: "pending" | "processing" | "completed" | "failed";
}

interface StartCollectResponse {
  status: "pending" | "processing" | "completed" | "failed";
  startedAt: Date | null;
}

class TaskService {
  private dbRepo: DBRepo;

  constructor(dbRepoInstance?: DBRepo) {
    this.dbRepo = dbRepoInstance || dbRepo;
  }

  async createTask(taskData: CreateTaskRequest): Promise<CreateTaskResponse> {
    try {
      // Создаем задачу с новой структурой данных
      const taskCreationData = {
        type: taskData.type || ('fetch_comments' as "fetch_comments" | "process_groups" | "analyze_posts"),
        priority: 0,
        groups: taskData.groupIds || [],
        parameters: taskData.options || {},
        metadata: {
          ...taskData.options,
          groupIds: taskData.groupIds,
          postUrls: taskData.postUrls
        },
        status: 'pending' as "pending" | "processing" | "completed" | "failed",
        createdBy: 'system'
      };

      const task = await this.dbRepo.createTask(taskCreationData);
      return { taskId: task.id, status: task.status };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to create task', { error: errorMsg });
      throw new Error(`Failed to create task: ${errorMsg}`);
    }
  }

  async getTaskById(taskId: number): Promise<any | null> {
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

      // Обновляем статус задачи на processing
      await this.dbRepo.updateTask(taskId, {
        status: 'processing',
        startedAt: new Date()
      });

      // Note: Background collection is now handled by BullMQ queue
      // This method is for manual task starts if needed

      const updatedTask = await this.dbRepo.getTaskById(taskId);
      return { status: 'processing', startedAt: updatedTask.startedAt };
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

      // Безопасно извлекаем метрики из metrics JSON поля
      const metricsData = task.metrics as any || {};
      const metrics: TaskMetrics = {
        posts: metricsData.posts || 0,
        comments: metricsData.comments || 0,
        errors: metricsData.errors || []
      };

      return {
        status: task.status,
        type: task.type,
        priority: task.priority,
        progress: task.progress,
        metrics,
        errors: metrics.errors,
        groups: (task.groups as any) || [],
        parameters: (task.parameters as any) || {},
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
    status?: "pending" | "processing" | "completed" | "failed",
    type?: "fetch_comments" | "process_groups" | "analyze_posts"
  ): Promise<ListTasksResult> {
    try {
      const offset = (page - 1) * limit;
      const options: ListTasksOptions = {
        limit,
        offset,
        ...(status && { status }),
        ...(type && { type })
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

      const updateData: any = {
        progress: Math.min(100, Math.max(0, progress))
      };

      if (metadata) {
        const currentMetrics = (task.metrics as any) || {};
        updateData.metrics = { ...currentMetrics, ...metadata };
      }

      await this.dbRepo.updateTask(taskId, updateData);

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

      await this.dbRepo.updateTask(taskId, {
        status: 'completed',
        result,
        finishedAt: new Date(),
        progress: 100
      });
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

      await this.dbRepo.updateTask(taskId, {
        status: 'failed',
        error: errorMessage,
        finishedAt: new Date()
      });
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
  async getTaskStats(): Promise<Record<"pending" | "processing" | "completed" | "failed", number>> {
    try {
      return await this.dbRepo.getTaskStats();
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get task stats', { error: errorMsg });
      throw new Error(`Failed to get task stats: ${errorMsg}`);
    }
  }

  /**
   * Обновляет статус задачи с временной меткой
   * Используется BullMQ worker для обновления статуса
   */
  async updateTaskStatus(taskId: number, status: "pending" | "processing" | "completed" | "failed", timestamp?: Date): Promise<void> {
    try {
      const task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        throw new Error('Task not found');
      }

      const updateData: any = { status };

      // Устанавливаем временные метки в зависимости от статуса
      if (status === 'processing' && !task.startedAt) {
        updateData.startedAt = timestamp || new Date();
      } else if (status === 'completed' || status === 'failed') {
        updateData.finishedAt = timestamp || new Date();
        if (status === 'completed') {
          updateData.progress = 100;
        }
      }

      await this.dbRepo.updateTask(taskId, updateData);

      logger.info('Task status updated', { taskId, status, timestamp });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to update task status', { taskId, status, error: errorMsg });
      throw new Error(`Failed to update task status: ${errorMsg}`);
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