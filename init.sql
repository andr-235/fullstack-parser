-- Create database if not exists
CREATE DATABASE IF NOT EXISTS vk_analyzer;

-- Connect to vk_analyzer
\c vk_analyzer;

-- Create tables
CREATE TABLE IF NOT EXISTS "Tasks" (
  "id" SERIAL PRIMARY KEY,
  "status" VARCHAR(50) DEFAULT 'pending',
  "groups" JSONB,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "Posts" (
  "id" SERIAL PRIMARY KEY,
  "taskId" INTEGER REFERENCES "Tasks"(id) ON DELETE CASCADE,
  "groupId" INTEGER,
  "postId" INTEGER UNIQUE,
  "text" TEXT,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "Comments" (
  "id" SERIAL PRIMARY KEY,
  "postId" INTEGER REFERENCES "Posts"(id) ON DELETE CASCADE,
  "text" TEXT,
  "authorId" INTEGER,
  "date" TIMESTAMP,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tasks_status ON "Tasks" (status);
CREATE INDEX IF NOT EXISTS idx_posts_taskId ON "Posts" (taskId);
CREATE INDEX IF NOT EXISTS idx_comments_postId ON "Comments" (postId);