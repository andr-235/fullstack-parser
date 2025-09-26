import dbRepo from '../../src/repositories/dbRepo';

// Mock Sequelize models
const mockPost = {
  bulkCreate: jest.fn(),
  findAll: jest.fn(),
  count: jest.fn()
};

const mockComment = {
  bulkCreate: jest.fn(),
  findAll: jest.fn()
};

const mockTask = {
  create: jest.fn(),
  findByPk: jest.fn(),
  update: jest.fn(),
  findAll: jest.fn(),
  count: jest.fn()
};

const mockLogger = {
  error: jest.fn()
};

jest.mock('../../src/utils/logger.ts', () => mockLogger);

// Mock Sequelize models
jest.mock('../../src/models/index.ts', () => ({
  sequelize: {},
  Post: mockPost,
  Comment: mockComment,
  Task: mockTask
}));

describe('DBRepo', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('upsertPosts', () => {
    it('should upsert posts with correct parameters', async () => {
      const taskId = 1;
      const posts = [
        {
          vk_post_id: 123,
          owner_id: -12345,
          group_id: 12345,
          text: 'Test post',
          date: new Date(),
          likes: 5
        },
        {
          vk_post_id: 124,
          owner_id: -12345,
          group_id: 12345,
          text: 'Another post',
          date: new Date(),
          likes: 10
        }
      ];

      const mockCreatedPosts = posts.map(post => ({ ...post, taskId, id: Math.random() }));
      mockPost.bulkCreate.mockResolvedValue(mockCreatedPosts);

      const result = await dbRepo.upsertPosts(taskId, posts);

      expect(mockPost.bulkCreate).toHaveBeenCalledWith(
        posts.map(post => ({ ...post, taskId })),
        {
          updateOnDuplicate: ['text', 'date', 'likes', 'owner_id', 'group_id', 'updatedAt'],
          ignoreDuplicates: false
        }
      );

      expect(result).toEqual(mockCreatedPosts);
    });

    it('should handle database errors gracefully', async () => {
      const taskId = 1;
      const posts = [{ vk_post_id: 123, text: 'Test' }];

      const dbError = new Error('Unique constraint violation');
      mockPost.bulkCreate.mockRejectedValue(dbError);

      await expect(dbRepo.upsertPosts(taskId, posts)).rejects.toThrow('Failed to upsert posts: Unique constraint violation');

      expect(mockLogger.error).toHaveBeenCalledWith('Failed to upsert posts', {
        taskId,
        error: 'Unique constraint violation'
      });
    });
  });

  describe('upsertComments', () => {
    it('should upsert comments with correct parameters', async () => {
      const postVkId = 123;
      const comments = [
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

      const mockCreatedComments = comments.map(comment => ({ ...comment, id: Math.random() }));
      mockComment.bulkCreate.mockResolvedValue(mockCreatedComments);

      const result = await dbRepo.upsertComments(postVkId, comments);

      expect(mockComment.bulkCreate).toHaveBeenCalledWith(comments, {
        updateOnDuplicate: ['text', 'date', 'likes', 'author_id', 'author_name', 'updatedAt'],
        ignoreDuplicates: false
      });

      expect(result).toEqual(mockCreatedComments);
    });

    it('should handle database errors gracefully', async () => {
      const postVkId = 123;
      const comments = [{ vk_comment_id: 456, text: 'Test comment' }];

      const dbError = new Error('Database connection failed');
      mockComment.bulkCreate.mockRejectedValue(dbError);

      await expect(dbRepo.upsertComments(postVkId, comments)).rejects.toThrow('Failed to upsert comments: Database connection failed');

      expect(mockLogger.error).toHaveBeenCalledWith('Failed to upsert comments', {
        postVkId,
        error: 'Database connection failed'
      });
    });
  });

  describe('createTask', () => {
    it('should create task with correct parameters', async () => {
      const taskData = {
        groups: [12345, 67890],
        status: 'created',
        metrics: { posts: 0, comments: 0, errors: [] }
      };

      const mockTask = { id: 1, ...taskData, groups: JSON.stringify(taskData.groups) };
      mockTask.create.mockResolvedValue(mockTask);

      const result = await dbRepo.createTask(taskData.groups);

      expect(mockTask.create).toHaveBeenCalledWith({
        status: 'pending',
        groups: JSON.stringify(taskData.groups)
      });

      expect(result).toEqual(mockTask);
    });
  });

  describe('updateTask', () => {
    it('should update task with correct parameters', async () => {
      const taskId = 1;
      const updates = {
        status: 'completed',
        metrics: { posts: 5, comments: 15, errors: [] }
      };

      const mockUpdatedTask = { id: taskId, ...updates };
      mockTask.update.mockResolvedValue([1]); // Number of affected rows
      mockTask.findByPk.mockResolvedValue(mockUpdatedTask);

      const result = await dbRepo.updateTask(taskId, updates);

      expect(mockTask.update).toHaveBeenCalledWith(updates, {
        where: { id: taskId },
        returning: true
      });

      expect(mockTask.findByPk).toHaveBeenCalledWith(taskId);
      expect(result).toEqual(mockUpdatedTask);
    });

    it('should throw error when task not found', async () => {
      const taskId = 999;
      const updates = { status: 'completed' };

      mockTask.update.mockResolvedValue([0]); // No rows affected

      await expect(dbRepo.updateTask(taskId, updates)).rejects.toThrow('Task with id 999 not found');

      expect(mockLogger.error).toHaveBeenCalledWith('Failed to update task', {
        taskId,
        error: 'Task with id 999 not found'
      });
    });
  });

  describe('getTaskById', () => {
    it('should return task when found', async () => {
      const taskId = 1;
      const mockTask = {
        id: taskId,
        status: 'completed',
        groups: '[12345, 67890]',
        metrics: '{"posts": 5, "comments": 15}'
      };

      mockTask.findByPk.mockResolvedValue(mockTask);

      const result = await dbRepo.getTaskById(taskId);

      expect(mockTask.findByPk).toHaveBeenCalledWith(taskId);
      expect(result).toEqual(mockTask);
    });

    it('should throw error when task not found', async () => {
      const taskId = 999;

      mockTask.findByPk.mockResolvedValue(null);

      await expect(dbRepo.getTaskById(taskId)).rejects.toThrow('Task with id 999 not found');
    });
  });

  describe('getResults', () => {
    it('should return posts with comments for a task', async () => {
      const taskId = 1;
      const groupId = 12345;
      const postId = 123;

      const mockPosts = [
        {
          id: 1,
          vk_post_id: 123,
          text: 'Test post',
          comments: [
            { id: 1, text: 'Comment 1' },
            { id: 2, text: 'Comment 2' }
          ]
        }
      ];

      mockPost.findAll.mockResolvedValue(mockPosts);

      const result = await dbRepo.getResults(taskId, groupId, postId);

      expect(mockPost.findAll).toHaveBeenCalledWith({
        where: {
          taskId,
          id: postId,
          groupId
        },
        include: [{
          model: mockComment,
          as: 'comments'
        }]
      });

      expect(result).toEqual({
        posts: mockPosts,
        totalComments: 2
      });
    });

    it('should handle optional parameters correctly', async () => {
      const taskId = 1;

      mockPost.findAll.mockResolvedValue([]);

      await dbRepo.getResults(taskId);

      expect(mockPost.findAll).toHaveBeenCalledWith({
        where: { taskId },
        include: [{
          model: mockComment,
          as: 'comments'
        }]
      });
    });
  });
});