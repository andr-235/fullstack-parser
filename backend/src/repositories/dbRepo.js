const winston = require('winston');
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

  async listTasks({ limit, offset }) {
    const tasks = await this.Task.findAll({
      limit,
      offset,
      order: [['createdAt', 'DESC']],
    });
    const total = await this.Task.count();
    return { tasks, total };
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