-- Create tables for the VK analyzer application

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
  id SERIAL PRIMARY KEY,
  status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  type VARCHAR(30) NOT NULL DEFAULT 'fetch_comments' CHECK (type IN ('fetch_comments', 'process_groups', 'analyze_posts')),
  priority INTEGER NOT NULL DEFAULT 0 CHECK (priority >= 0 AND priority <= 10),
  progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
  groups JSONB,
  metrics JSONB,
  parameters JSONB,
  result JSONB,
  error TEXT,
  executionTime INTEGER,
  startedAt TIMESTAMP,
  finishedAt TIMESTAMP,
  createdBy VARCHAR(100) DEFAULT 'system',
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create posts table
CREATE TABLE IF NOT EXISTS posts (
  id SERIAL PRIMARY KEY,
  vk_post_id INTEGER NOT NULL UNIQUE,
  owner_id INTEGER NOT NULL,
  group_id INTEGER NOT NULL,
  text TEXT NOT NULL DEFAULT '',
  date TIMESTAMP NOT NULL,
  likes INTEGER NOT NULL DEFAULT 0,
  taskId INTEGER NOT NULL,
  ownerId INTEGER,
  groupId INTEGER,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create comments table
CREATE TABLE IF NOT EXISTS comments (
  id SERIAL PRIMARY KEY,
  vk_comment_id INTEGER NOT NULL UNIQUE,
  post_vk_id INTEGER NOT NULL,
  owner_id INTEGER NOT NULL,
  author_id INTEGER NOT NULL,
  author_name VARCHAR(255) NOT NULL,
  text TEXT NOT NULL DEFAULT '',
  date TIMESTAMP NOT NULL,
  likes INTEGER NOT NULL DEFAULT 0,
  userId INTEGER,
  postId INTEGER,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create groups table
CREATE TABLE IF NOT EXISTS groups (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  status VARCHAR(10) DEFAULT 'valid' CHECK (status IN ('valid', 'invalid', 'duplicate')),
  taskId UUID NOT NULL,
  uploadedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks (type);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks (createdAt);
CREATE INDEX IF NOT EXISTS idx_tasks_status_priority ON tasks (status, priority);
CREATE INDEX IF NOT EXISTS idx_tasks_type_status ON tasks (type, status);
CREATE INDEX IF NOT EXISTS idx_posts_task_id ON posts (taskId);
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments (post_vk_id);