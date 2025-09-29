// Переиспользуем типы из Prisma Client
export type {
  posts as PostAttributes,
  comments as CommentAttributes,
  groups as GroupAttributes,
  tasks as TaskAttributes
} from '@prisma/client';

// Типы для создания записей (без полей автогенерации)
export interface PostCreationAttributes {
  vk_id: number;
  owner_id: number;
  from_id: number;
  date: Date;
  text: string;
  likes_count: number;
  reposts_count: number;
  comments_count: number;
  views_count: number;
  attachments: any[];
  task_id: number;
}

export interface CommentCreationAttributes {
  vk_id: number;
  post_id: number;
  from_id: number;
  date: Date;
  text: string;
  reply_to_user: number | null;
  reply_to_comment: number | null;
  likes_count: number;
  thread_count: number;
  attachments: any[];
}

export interface GroupCreationAttributes {
  vk_id: number;
  name?: string | null;
  screen_name?: string | null;
  photo_50?: string | null;
  members_count?: number | null;
  is_closed?: number;
  description?: string | null;
  task_id: string;
}

export interface TaskCreationAttributes {
  type: string;
  status: string;
  progress: number;
  error_message?: string | null;
  data: any;
}

// Базовый интерфейс для моделей с timestamps
export interface ModelWithTimestamps {
  createdAt: Date;
  updatedAt: Date;
}

export type Environment = 'development' | 'production' | 'test';

// Обновленная конфигурация для Prisma
export interface DatabaseConfig {
  username: string;
  password: string;
  database: string;
  host: string;
  port: number;
  dialect: 'postgresql' | 'mysql' | 'sqlite';
  logging?: boolean | ((sql: string) => void);
  pool?: {
    max: number;
    min: number;
    acquire: number;
    idle: number;
    evict?: number;
  };
  define?: {
    timestamps: boolean;
    underscored: boolean;
    freezeTableName: boolean;
  };
}

// Типы для пагинации и фильтрации
export interface PaginationOptions {
  page?: number;
  limit?: number;
  offset?: number;
}

export interface SortOptions {
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface FilterOptions {
  status?: string;
  search?: string;
  dateFrom?: Date;
  dateTo?: Date;
}

// Псевдоним для совместимости с существующим кодом
export type SequelizeConfig = DatabaseConfig;