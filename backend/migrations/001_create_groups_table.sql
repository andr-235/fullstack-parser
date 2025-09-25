-- Migration: Create groups table
-- Created: 2024-01-15
-- Description: Creates groups table for storing VK groups from file uploads

CREATE TABLE IF NOT EXISTS groups (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255),
  status VARCHAR(20) DEFAULT 'valid' CHECK (status IN ('valid', 'invalid', 'duplicate')),
  task_id UUID NOT NULL,
  uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Create index on task_id for faster queries
CREATE INDEX IF NOT EXISTS idx_groups_task_id ON groups(task_id);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_groups_status ON groups(status);

-- Create index on uploaded_at for sorting
CREATE INDEX IF NOT EXISTS idx_groups_uploaded_at ON groups(uploaded_at);

-- Add comment to table
COMMENT ON TABLE groups IS 'VK groups uploaded from files';
COMMENT ON COLUMN groups.id IS 'VK group ID (negative integer)';
COMMENT ON COLUMN groups.name IS 'VK group name (optional)';
COMMENT ON COLUMN groups.status IS 'Group status: valid, invalid, duplicate';
COMMENT ON COLUMN groups.task_id IS 'Upload task UUID';
COMMENT ON COLUMN groups.uploaded_at IS 'Upload timestamp';
