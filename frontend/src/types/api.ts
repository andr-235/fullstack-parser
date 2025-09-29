import type { AxiosResponse } from 'axios'

// Base types
export interface ApiError {
  message: string
  code?: string
  details?: any
}

export interface PaginationParams {
  page?: number
  limit?: number
  offset?: number
}

// Task types
export interface TaskCreateData {
  ownerId: string | number
  postId: string | number
  token: string
}

export interface VkCollectTaskData {
  groups: number[]
}

export interface TaskStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  errors?: string[]
}

export interface TaskProgress {
  processed: number
  total: number
}

export interface Task {
  id: string | number
  type: string
  status: TaskStatus['status']
  priority?: number
  progress?: TaskProgress
  errors?: string[]
  groups?: any[]
  parameters?: Record<string, any>
  result?: any
  error?: string | null
  executionTime?: number | null
  startedAt?: string | null
  finishedAt?: string | null
  completedAt?: string | null
  createdBy?: string
  createdAt: string
  updatedAt: string
}

export interface TasksResponse {
  tasks: Task[]
  total: number
  page: number
  totalPages: number
}

// Comments types
export interface Comment {
  id: string | number
  text: string
  authorId: string | number
  authorName: string
  date: string
  sentiment?: 'positive' | 'negative' | 'neutral'
  groupId?: string | number
  postId?: string | number
}

export interface CommentsParams extends PaginationParams {
  task_id: string | number
  groupId?: string | number | null
  postId?: string | number | null
  sentiment?: string
}

export interface CommentsResponse {
  results: Comment[]
  total: number
}

// Groups types
export interface Group {
  id: string | number
  name: string
  status: 'valid' | 'invalid' | 'duplicate'
  task_id: string
  uploaded_at: string
}

export interface GroupsParams extends PaginationParams {
  status?: string
  search?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface GroupsResponse {
  groups: Group[]
  total: number
}

export interface GroupUploadResponse {
  taskId: string | number
  message: string
}

// API response wrapper from backend
export interface ApiResponseWrapper<T = any> {
  success: boolean
  data: T
  error?: string
}

// Пагинированный ответ для списков
export interface PaginatedApiResponse<T = any> {
  success: boolean
  timestamp: string
  requestId: string
  data: T[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
    hasNext: boolean
    hasPrev: boolean
  }
}

// API response types
export type ApiResponse<T = any> = AxiosResponse<ApiResponseWrapper<T>>
export type PaginatedResponse<T = any> = AxiosResponse<PaginatedApiResponse<T>>

// API function types
export interface TasksApiType {
  getTasks: (params?: Partial<PaginationParams & { status?: string }>) => Promise<ApiResponse<TasksResponse>>
  createVkCollectTask: (data: VkCollectTaskData) => Promise<ApiResponse<{ taskId: string | number }>>
  getTaskDetails: (taskId: string | number) => Promise<ApiResponse<Task>>
}

export interface GroupsApiType {
  uploadGroups: (formData: FormData, encoding?: string) => Promise<ApiResponse<GroupUploadResponse>>
  getTaskStatus: (taskId: string | number) => Promise<ApiResponse<TaskStatus>>
  getGroups: (params?: GroupsParams) => Promise<PaginatedResponse<Group>>
  deleteGroup: (groupId: string | number) => Promise<ApiResponse<{ message: string }>>
  deleteGroups: (groupIds: (string | number)[]) => Promise<ApiResponse<{ message: string }>>
  getAllGroups: () => Promise<PaginatedResponse<Group>>
}