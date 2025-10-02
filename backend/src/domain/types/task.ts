export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type TaskType = 'fetch_comments' | 'process_groups' | 'analyze_posts';

export interface TaskAttributes {
  id: number;
  status: TaskStatus;
  type: TaskType;
  progress: number;
  startedAt: Date | null;
  completedAt: Date | null;
  metadata: Record<string, any>;
  error: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface TaskCreationAttributes {
  type: TaskType;
  metadata: Record<string, any>;
  status?: TaskStatus;
  progress?: number;
}

export interface CreateTaskRequest {
  type: TaskType;
  groupIds?: number[];
  postUrls?: string[];
  options?: {
    limit?: number;
    includeReplies?: boolean;
    filterWords?: string[];
    token?: string;
  };
}

export interface TaskProgressUpdate {
  progress: number;
  status: TaskStatus;
  error?: string;
}

export interface TaskResponse {
  taskId: number;
  status: TaskStatus;
  progress: number;
  startedAt: Date | null;
  completedAt: Date | null;
  error: string | null;
  result?: any;
}

export interface BullJobData {
  taskId: number;
  type: TaskType;
  metadata: Record<string, any>;
}

export interface JobProgress {
  percentage: number;
  message?: string;
  processedItems?: number;
  totalItems?: number;
}

/**
 * Метрики для точного расчета прогресса задач
 */
export interface TaskMetrics {
  /** Общее количество групп для обработки */
  groupsTotal: number;
  /** Количество обработанных групп */
  groupsProcessed: number;
  /** Общее количество постов */
  postsTotal: number;
  /** Количество обработанных постов */
  postsProcessed: number;
  /** Общее количество комментариев (точное или оценочное) */
  commentsTotal: number;
  /** Количество обработанных комментариев */
  commentsProcessed: number;
  /** Среднее количество комментариев на пост для оценки */
  estimatedCommentsPerPost: number;
}

/**
 * Результат расчета прогресса с детализацией по фазам
 */
export interface ProgressResult {
  /** Количество обработанных единиц (в процентах 0-100) */
  processed: number;
  /** Общее количество единиц (всегда 100 для процентной системы) */
  total: number;
  /** Процент выполнения (0-100) */
  percentage: number;
  /** Текущая фаза обработки */
  phase: 'groups' | 'posts' | 'comments';
  /** Детальная информация о каждой фазе */
  phases: {
    groups: { weight: number; progress: number; completed: boolean };
    posts: { weight: number; progress: number; completed: boolean };
    comments: { weight: number; progress: number; completed: boolean };
  };
}