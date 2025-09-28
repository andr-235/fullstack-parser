// Jest setup file for TypeScript tests
import { beforeAll, afterAll } from '@jest/globals';
import path from 'path';
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, '../.env') });

// Set test environment variables
process.env.NODE_ENV = 'test';
process.env.DATABASE_URL = process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/vk_analyzer_test';
process.env.REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
process.env.VK_TOKEN = process.env.VK_TOKEN || 'test-token';

// Global test setup
beforeAll(async () => {
  // Setup test environment
});

afterAll(async () => {
  // Cleanup test environment
});