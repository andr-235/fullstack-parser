// Mock VKService class since it's an ES6 module
const mockVKService = {
  collectForTask: jest.fn(),
  getResults: jest.fn()
};

// Mock dependencies modules with factories
jest.mock('../../src/repositories/vkApi.ts', () => ({
  default: {
    getPosts: jest.fn(),
    getComments: jest.fn()
  }
}));

jest.mock('../../src/repositories/dbRepo.ts', () => ({
  default: {
    getTaskById: jest.fn(),
    upsertPosts: jest.fn(),
    upsertComments: jest.fn(),
    getResults: jest.fn()
  }
}));

jest.mock('../../src/utils/logger.ts', () => ({
  default: {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn()
  }
}));

import VKService from '../../src/services/vkService';
import vkApi from '../../src/repositories/vkApi';
import dbRepo from '../../src/repositories/dbRepo';
import logger from '../../src/utils/logger';

describe('VKService', () => {
  let vkService: VKService;

  beforeEach(() => {
    jest.clearAllMocks();

    // Reset mocks
    vkApi.getPosts.mockResolvedValue({ posts: [] });
    vkApi.getComments.mockResolvedValue({ comments: [] });
    dbRepo.getTaskById.mockResolvedValue({
      markAsProcessing: jest.fn().mockResolvedValue(),
      updateProgress: jest.fn().mockResolvedValue(),
      markAsCompleted: jest.fn().mockResolvedValue(),
      markAsFailed: jest.fn().mockResolvedValue(),
      save: jest.fn().mockResolvedValue()
    });
    dbRepo.upsertPosts.mockResolvedValue();
    dbRepo.upsertComments.mockResolvedValue();
    dbRepo.getResults.mockResolvedValue({ posts: [], totalComments: 0 });

    // Create VKService instance with mocked dependencies
    vkService = new VKService(vkApi, dbRepo);
  });

  describe('collectForTask', () => {
    const mockPosts = [
      {
        vk_post_id: 123,
        owner_id: -12345,
        group_id: 12345,
        text: 'Test post',
        date: new Date(),
        likes: 5
      }
    ];

    const mockComments = [
      {
        vk_comment_id: 456,
        post_vk_id: 123,
        owner_id: -12345,
        author_id: 789,
        author_name: 'John Doe',
        text: 'Great post!',
        date: new Date(),
        likes: 2
      }
    ];

    beforeEach(() => {
      vkApi.getPosts.mockResolvedValue({ posts: mockPosts });
      vkApi.getComments.mockResolvedValue({ comments: mockComments });
      dbRepo.getTaskById.mockResolvedValue({
        markAsProcessing: jest.fn().mockResolvedValue(),
        updateProgress: jest.fn().mockResolvedValue(),
        markAsCompleted: jest.fn().mockResolvedValue(),
        markAsFailed: jest.fn().mockResolvedValue(),
        save: jest.fn().mockResolvedValue()
      });
      dbRepo.upsertPosts.mockResolvedValue();
      dbRepo.upsertComments.mockResolvedValue();
    });

    it('should successfully collect posts and comments for groups', async () => {
      const taskId = 1;
      const groups = [12345, 67890];

      await vkService.collectForTask(taskId, groups);

      // Should call getTaskById
      expect(dbRepo.getTaskById).toHaveBeenCalledWith(taskId);

      // Should update task status to processing
      expect(dbRepo.getTaskById().mock.results[0].value.markAsProcessing).toHaveBeenCalled();

      // Should call VK API for each group
      expect(vkApi.getPosts).toHaveBeenCalledTimes(2);
      expect(vkApi.getPosts).toHaveBeenCalledWith(12345);
      expect(vkApi.getPosts).toHaveBeenCalledWith(67890);

      // Should upsert posts for each group
      expect(dbRepo.upsertPosts).toHaveBeenCalledTimes(2);

      // Should get comments for each post
      expect(vkApi.getComments).toHaveBeenCalledTimes(2);

      // Should upsert comments
      expect(dbRepo.upsertComments).toHaveBeenCalledTimes(2);

      // Should update task with final status
      expect(dbRepo.getTaskById().mock.results[0].value.markAsCompleted).toHaveBeenCalled();
    });

    it('should handle negative group IDs correctly', async () => {
      const taskId = 1;
      const groups = [-12345, '-67890'];

      await vkService.collectForTask(taskId, groups);

      // Should normalize group IDs to positive
      expect(vkApi.getPosts).toHaveBeenCalledWith(12345);
      expect(vkApi.getPosts).toHaveBeenCalledWith(67890);
    });

    it('should limit posts to first 10', async () => {
      const taskId = 1;
      const groups = [12345];

      // Mock 15 posts
      const manyPosts = Array.from({ length: 15 }, (_, i) => ({
        vk_post_id: i + 1,
        owner_id: -12345,
        group_id: 12345,
        text: `Post ${i + 1}`,
        date: new Date(),
        likes: i
      }));

      vkApi.getPosts.mockResolvedValue({ posts: manyPosts });

      await vkService.collectForTask(taskId, groups);

      // Should only process first 10 posts
      expect(dbRepo.upsertPosts).toHaveBeenCalledWith(taskId, manyPosts.slice(0, 10));
      expect(vkApi.getComments).toHaveBeenCalledTimes(10);
    });

    it('should handle VK API errors gracefully', async () => {
      const taskId = 1;
      const groups = [12345, 67890];

      vkApi.getPosts
        .mockRejectedValueOnce(new Error('VK API error for group 12345'))
        .mockResolvedValueOnce({ posts: mockPosts });

      await vkService.collectForTask(taskId, groups);

      // Should continue processing other groups
      expect(vkApi.getPosts).toHaveBeenCalledTimes(2);

      // Should mark task as failed due to errors
      expect(dbRepo.getTaskById().mock.results[0].value.markAsFailed).toHaveBeenCalled();
    });

    it('should handle comment API errors without failing entire task', async () => {
      const taskId = 1;
      const groups = [12345];

      vkApi.getComments.mockRejectedValue(new Error('Comments API error'));

      await vkService.collectForTask(taskId, groups);

      // Should still upsert posts
      expect(dbRepo.upsertPosts).toHaveBeenCalled();

      // Should log error but not fail entire task for posts processing
      expect(logger.error).toHaveBeenCalledWith(
        'Error getting comments for post',
        expect.objectContaining({
          groupId: 12345,
          postId: 123,
          error: 'Comments API error'
        })
      );

      // Should mark task as failed due to comment errors
      expect(dbRepo.getTaskById().mock.results[0].value.markAsFailed).toHaveBeenCalled();
    });

    it('should update progress periodically', async () => {
      const taskId = 1;
      const groups = [12345];

      await vkService.collectForTask(taskId, groups);

      // Should update progress after processing each group
      expect(dbRepo.getTaskById().mock.results[0].value.updateProgress).toHaveBeenCalled();
    });

    it('should handle critical errors and update task status', async () => {
      const taskId = 1;
      const groups = [12345];

      const criticalError = new Error('Critical database error');
      dbRepo.getTaskById.mockResolvedValueOnce({
        markAsProcessing: jest.fn().mockResolvedValue(),
        updateProgress: jest.fn().mockResolvedValue(),
        markAsFailed: jest.fn().mockResolvedValue(criticalError),
        save: jest.fn().mockResolvedValue()
      });

      await expect(vkService.collectForTask(taskId, groups)).rejects.toThrow('Critical database error');

      // Should attempt to update task status to failed
      expect(dbRepo.getTaskById().mock.results[0].value.markAsFailed).toHaveBeenCalled();
    });

    it('should handle undefined posts gracefully', async () => {
      const taskId = 1;
      const groups = [12345];

      vkApi.getPosts.mockResolvedValue({ posts: undefined });

      await vkService.collectForTask(taskId, groups);

      expect(logger.warn).toHaveBeenCalledWith('No items in VK posts response', expect.any(Object));
      expect(logger.info).toHaveBeenCalledWith('Posts received for processing', expect.objectContaining({ count: 0 }));
      expect(dbRepo.upsertPosts).toHaveBeenCalledWith(taskId, []);
      expect(vkApi.getComments).not.toHaveBeenCalled();
    });
  });

  describe('getResults', () => {
    it('should delegate to dbRepo.getResults', async () => {
      const taskId = 1;
      const groupId = 12345;
      const postId = 123;

      const mockResults = { posts: [], totalComments: 0 };
      dbRepo.getResults.mockResolvedValue(mockResults);

      const result = await vkService.getResults(taskId, groupId, postId);

      expect(dbRepo.getResults).toHaveBeenCalledWith(taskId, groupId, postId);
      expect(result).toBe(mockResults);
    });
  });
});