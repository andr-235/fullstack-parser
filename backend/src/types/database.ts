import { Optional, Model } from 'sequelize';

export interface PostAttributes {
  id: number;
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
  createdAt: Date;
  updatedAt: Date;
}

export interface PostCreationAttributes extends Optional<PostAttributes, 'id' | 'createdAt' | 'updatedAt'> {}

export interface CommentAttributes {
  id: number;
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
  createdAt: Date;
  updatedAt: Date;
}

export interface CommentCreationAttributes extends Optional<CommentAttributes, 'id' | 'createdAt' | 'updatedAt'> {}

export interface GroupAttributes {
  id: number;
  vk_id: number;
  name: string;
  screen_name: string;
  type: string;
  is_closed: number;
  photo_url: string | null;
  description: string | null;
  members_count: number | null;
  source_file: string | null;
  task_id: number | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface GroupCreationAttributes extends Optional<GroupAttributes, 'id' | 'createdAt' | 'updatedAt'> {}

export interface ModelWithTimestamps extends Model {
  createdAt: Date;
  updatedAt: Date;
}

export type Environment = 'development' | 'production' | 'test';

export interface SequelizeConfig {
  username: string;
  password: string;
  database: string;
  host: string;
  port: number;
  dialect: 'postgres' | 'mysql' | 'sqlite' | 'mariadb' | 'mssql';
  logging?: boolean | ((sql: string) => void);
  pool?: any;
  define?: any;
}