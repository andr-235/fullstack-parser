const logger = require('../utils/logger.js');

const { sequelize, Task, Post, Comment } = require('../models/index.js');

class DBRepo {
  constructor() {
    this.sequelize = sequelize;
    this.Task = Task;
    this.Post = Post;
    this.Comment = Comment;
  }

  async createTask(groups) {
    const task = await this.Task.create({
      status: 'pending',
      groups: JSON.stringify(groups),
    });
    return task;
  }

  async getTaskById(taskId) {
    const task = await this.Task.findByPk(taskId);
    if (!task) {
      throw new Error(`Task with id ${taskId} not found`);
    }
    return task;
  }

  async updateTask(taskId, updates) {
    const [updated] = await this.Task.update(updates, {
      where: { id: taskId },
      returning: true,
    });
    if (!updated) {
      logger.error('Failed to update task', { taskId, error: `Task with id ${taskId} not found` });
      throw new Error(`Task with id ${taskId} not found`);
    }
    return await this.Task.findByPk(taskId);
  }

  async createPosts(taskId, posts) {
    const taskPosts = posts.map(post => ({
      ...post,
      taskId,
    }));
    const createdPosts = await this.Post.bulkCreate(taskPosts);
    return createdPosts;
  }

  async createComments(postId, comments) {
    const postComments = comments.map(comment => ({
      ...comment,
      postId,
    }));
    const createdComments = await this.Comment.bulkCreate(postComments);
    return createdComments;
  }

  async upsertPosts(taskId, posts) {
    const taskPosts = posts.map(post => ({
      ...post,
      taskId,
    }));

    try {
      const createdPosts = await this.Post.bulkCreate(taskPosts, {
        updateOnDuplicate: ['text', 'date', 'likes', 'owner_id', 'group_id', 'updatedAt'],
        ignoreDuplicates: false
      });
      return createdPosts;
    } catch (error) {
      logger.error('Failed to upsert posts', { taskId, error: error.message });
      throw new Error(`Failed to upsert posts: ${error.message}`);
    }
  }

  async upsertComments(postVkId, comments) {
    try {
      // Найти пост по vk_post_id для связи с комментариями
      const post = await this.Post.findOne({ where: { vk_post_id: postVkId } });
      if (!post) {
        throw new Error(`Post with vk_post_id ${postVkId} not found`);
      }

      // Добавить postId к комментариям для корректной ассоциации
      const commentsWithPostId = comments.map(comment => ({
        ...comment,
        postId: post.id // Связь через внутренний ID поста
      }));

      const createdComments = await this.Comment.bulkCreate(commentsWithPostId, {
        updateOnDuplicate: ['text', 'date', 'likes', 'author_id', 'author_name', 'updatedAt'],
        ignoreDuplicates: false
      });
      return createdComments;
    } catch (error) {
      logger.error('Failed to upsert comments', { postVkId, error: error.message });
      throw new Error(`Failed to upsert comments: ${error.message}`);
    }
  }

  /**
   * Получает список задач с пагинацией и опциональными фильтрами.
   * @param {Object} options - Опции запроса
   * @param {number} options.limit - Лимит задач на страницу
   * @param {number} options.offset - Смещение для пагинации
   * @param {string} [options.status] - Фильтр по статусу (pending, processing, completed, failed)
   * @param {string} [options.type] - Фильтр по типу (fetch_comments, process_groups, analyze_posts)
   * @returns {Promise<{tasks: Array, total: number}>} Список задач и общее количество
   */
  async listTasks({ limit, offset, status, type }) {
    const where = {};
    if (status) {
      where.status = status;
    }
    if (type) {
      where.type = type;
    }

    const tasks = await this.Task.findAll({
      where,
      limit,
      offset,
      order: [['createdAt', 'DESC']],
    });

    const totalCount = await this.Task.count({ where });
    return { tasks, total: totalCount };
  }

  async getResults(taskId, groupId = null, postId = null) {
    let whereClause = { taskId };
    if (postId) {
      whereClause.id = postId;
    }
    if (groupId) {
      whereClause.groupId = groupId;
    }

    const posts = await this.Post.findAll({
      where: whereClause,
      include: [{
        model: Comment,
        as: 'comments'
      }]
    });

    const totalComments = posts.reduce((sum, post) => sum + (post.comments?.length || 0), 0);

    return {
      posts,
      totalComments,
    };
  }
}

module.exports = new DBRepo();