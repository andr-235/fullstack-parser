// Mock VKService class since it's an ES6 module
const mockVKService = {
  collectForTask: jest.fn(),
  getResults: jest.fn()
};

// Mock the ES6 module
jest.mock('../../src/services/vkService.js', () => ({
  default: mockVKService
}));

// Mock dependencies
const mockVkApi = {
  getPosts: jest.fn(),
  getComments: jest.fn()
};

const mockDbRepo = {
  updateTask: jest.fn(),
  upsertPosts: jest.fn(),
  upsertComments: jest.fn()
};

const mockLogger = {
  info: jest.fn(),
  error: jest.fn()
};

jest.mock('../../src/utils/logger.js', () => mockLogger);

describe('VKService', () => {
  let vkService;

  beforeEach(() => {
    jest.clearAllMocks();

    // Create VKService instance with mocked dependencies
    const VKServiceClass = VKService.constructor;
    vkService = new VKServiceClass(mockVkApi, mockDbRepo);
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
      mockVkApi.getPosts.mockResolvedValue({ posts: mockPosts });
      mockVkApi.getComments.mockResolvedValue({ comments: mockComments });
      mockDbRepo.updateTask.mockResolvedValue();
      mockDbRepo.upsertPosts.mockResolvedValue();
      mockDbRepo.upsertComments.mockResolvedValue();
    });

    it('should successfully collect posts and comments for groups', async () => {
      const taskId = 1;
      const groups = [12345, 67890];

      await vkService.collectForTask(taskId, groups);

      // Should update task status to in_progress
      expect(mockDbRepo.updateTask).toHaveBeenCalledWith(taskId, {
        status: 'in_progress',
        startedAt: expect.any(Date)
      });

      // Should call VK API for each group
      expect(mockVkApi.getPosts).toHaveBeenCalledTimes(2);
      expect(mockVkApi.getPosts).toHaveBeenCalledWith(12345);
      expect(mockVkApi.getPosts).toHaveBeenCalledWith(67890);

      // Should upsert posts for each group
      expect(mockDbRepo.upsertPosts).toHaveBeenCalledTimes(2);

      // Should get comments for each post
      expect(mockVkApi.getComments).toHaveBeenCalledTimes(2);

      // Should upsert comments
      expect(mockDbRepo.upsertComments).toHaveBeenCalledTimes(2);

      // Should update task with final status
      expect(mockDbRepo.updateTask).toHaveBeenLastCalledWith(taskId, {
        status: 'completed',
        metrics: {
          posts: 2,
          comments: 2,
          errors: []
        },
        finishedAt: expect.any(Date)
      });
    });

    it('should handle negative group IDs correctly', async () => {
      const taskId = 1;
      const groups = [-12345, '-67890'];

      await vkService.collectForTask(taskId, groups);

      // Should normalize group IDs to positive
      expect(mockVkApi.getPosts).toHaveBeenCalledWith(12345);
      expect(mockVkApi.getPosts).toHaveBeenCalledWith(67890);
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

      mockVkApi.getPosts.mockResolvedValue({ posts: manyPosts });

      await vkService.collectForTask(taskId, groups);

      // Should only process first 10 posts
      expect(mockDbRepo.upsertPosts).toHaveBeenCalledWith(taskId, manyPosts.slice(0, 10));
      expect(mockVkApi.getComments).toHaveBeenCalledTimes(10);
    });

    it('should handle VK API errors gracefully', async () => {
      const taskId = 1;
      const groups = [12345, 67890];

      mockVkApi.getPosts
        .mockRejectedValueOnce(new Error('VK API error for group 12345'))
        .mockResolvedValueOnce({ posts: mockPosts });

      await vkService.collectForTask(taskId, groups);

      // Should continue processing other groups
      expect(mockVkApi.getPosts).toHaveBeenCalledTimes(2);

      // Should mark task as failed due to errors
      expect(mockDbRepo.updateTask).toHaveBeenLastCalledWith(taskId, {
        status: 'failed',
        metrics: {
          posts: 1, // Only one group succeeded
          comments: 1,
          errors: ['Error processing group 12345: VK API error for group 12345']
        },
        finishedAt: expect.any(Date)
      });
    });

    it('should handle comment API errors without failing entire task', async () => {
      const taskId = 1;
      const groups = [12345];

      mockVkApi.getComments.mockRejectedValue(new Error('Comments API error'));

      await vkService.collectForTask(taskId, groups);

      // Should still upsert posts
      expect(mockDbRepo.upsertPosts).toHaveBeenCalled();

      // Should log error but not fail entire task for posts processing
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Error getting comments for post',
        expect.objectContaining({
          groupId: 12345,
          postId: 123,
          error: 'Comments API error'
        })
      );

      // Should mark task as failed due to comment errors
      expect(mockDbRepo.updateTask).toHaveBeenLastCalledWith(taskId, {
        status: 'failed',
        metrics: expect.objectContaining({
          errors: expect.arrayContaining([
            expect.stringContaining('Error getting comments for group 12345, post 123')
          ])
        }),
        finishedAt: expect.any(Date)
      });
    });

    it('should update progress periodically', async () => {
      const taskId = 1;
      const groups = [12345];

      await vkService.collectForTask(taskId, groups);

      // Should update progress after processing each group
      expect(mockDbRepo.updateTask).toHaveBeenCalledWith(taskId, {
        metrics: {
          posts: 1,
          comments: 1,
          errors: []
        }
      });
    });

    it('should handle critical errors and update task status', async () => {
      const taskId = 1;
      const groups = [12345];

      const criticalError = new Error('Critical database error');
      mockDbRepo.updateTask.mockRejectedValueOnce(criticalError);

      await expect(vkService.collectForTask(taskId, groups)).rejects.toThrow('Critical database error');

      // Should attempt to update task status to failed
      expect(mockDbRepo.updateTask).toHaveBeenCalledWith(taskId, {
        status: 'failed',
        metrics: { posts: 0, comments: 0, errors: expect.arrayContaining([
          'General error in collectForTask: Critical database error'
        ])},
        finishedAt: expect.any(Date)
      });
    });
  });

  describe('getResults', () => {
    it('should delegate to dbRepo.getResults', async () => {
      const taskId = 1;
      const groupId = 12345;
      const postId = 123;

      const mockResults = { posts: [], totalComments: 0 };
      mockDbRepo.getResults = jest.fn().mockResolvedValue(mockResults);

      const result = await vkService.getResults(taskId, groupId, postId);

      expect(mockDbRepo.getResults).toHaveBeenCalledWith(taskId, groupId, postId);
      expect(result).toBe(mockResults);
    });
  });
});