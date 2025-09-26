// Simple integration test to verify all modules work together
describe('Integration Test', () => {
  it('should load all main modules without errors', () => {
    expect(() => {
      const dbRepo = require('../../src/repositories/dbRepo');
      const vkService = require('../../src/services/vkService');
      const taskService = require('../../src/services/taskService');
      const { queue, worker } = require('../../config/queue');
      const taskController = require('../../src/controllers/taskController');

      // Basic checks
      expect(dbRepo).toBeDefined();
      expect(vkService).toBeDefined();
      expect(taskService).toBeDefined();
      expect(queue).toBeDefined();
      expect(worker).toBeDefined();
      expect(taskController).toBeDefined();

      // Check that services have expected methods
      expect(typeof vkService.collectForTask).toBe('function');
      expect(typeof taskService.createTask).toBe('function');
      expect(typeof dbRepo.upsertPosts).toBe('function');
      expect(typeof dbRepo.upsertComments).toBe('function');

    }).not.toThrow();
  });

  it('should load models without errors', () => {
    expect(() => {
      const { sequelize, Post, Comment, Task } = require('../../src/models/index');

      expect(sequelize).toBeDefined();
      expect(Post).toBeDefined();
      expect(Comment).toBeDefined();
      expect(Task).toBeDefined();

      // Check model structures
      expect(Post.rawAttributes.vk_post_id).toBeDefined();
      expect(Comment.rawAttributes.vk_comment_id).toBeDefined();
      expect(Task.rawAttributes.finishedAt).toBeDefined();

    }).not.toThrow();
  });
});