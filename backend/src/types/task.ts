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