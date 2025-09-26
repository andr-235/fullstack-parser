import { Request } from 'express';

declare global {
  namespace Express {
    interface Request {
      id: string;
      startTime?: number;
    }
  }
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ValidationError extends Error {
  name: 'ValidationError';
  details: Array<{
    message: string;
    path: string[];
    type: string;
    context?: any;
  }>;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}