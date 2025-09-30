export interface Logger {
  info(message: string, meta?: any): void;
  error(message: string, error?: Error | any, meta?: any): void;
  warn(message: string, meta?: any): void;
  debug(message: string, meta?: any): void;
}

export interface FileUpload {
  fieldname: string;
  originalname: string;
  encoding: string;
  mimetype: string;
  size: number;
  buffer: Buffer;
}

export interface ProcessedGroup {
  id?: number;
  name: string;
  screenName?: string;
  url?: string;
  error?: string;
}

export interface FileParseResult {
  groups: ProcessedGroup[];
  errors: string[];
  totalProcessed: number;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  data?: any;
}

export interface RetryOptions {
  retries: number;
  delay: number;
  backoff?: 'linear' | 'exponential';
  maxDelay?: number;
}

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: Date;
}

export type LogLevel = 'error' | 'warn' | 'info' | 'debug';

export interface ConfigOptions {
  database: {
    host: string;
    port: number;
    username: string;
    password: string;
    database: string;
  };
  redis: {
    host: string;
    port: number;
    password?: string;
  };
  vk: {
    accessToken: string;
    apiVersion: string;
    requestsPerSecond: number;
  };
  server: {
    port: number;
    corsOrigins: string[];
  };
  logging: {
    level: LogLevel;
    format: 'json' | 'simple';
  };
}