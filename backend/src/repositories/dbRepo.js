const winston = require('winston');
const logger = require('../utils/logger');
const { sequelize, Task, Post, Comment } = require('../config/db');

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

  async updateTask(taskId, status, metrics = null) {
    const updateData = { status };
    if (metrics) {
      updateData.metrics = JSON.stringify(metrics);
    }
    const [updated] = await this.Task.update(updateData, {
      where: { id: taskId },
      returning: true,
    });
    if (!updated) {
      _error('Failed to update task', { taskId, error: `Task with id ${taskId} not found` });
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

  async getTaskStatus(taskId) {
    const task = await this.Task.findByPk(taskId);
    if (!task) {
      _error('Failed to get task status', { taskId, error: `Task with id ${taskId} not found` });
      throw new Error(`Task with id ${taskId} not found`);
    }
    return task;
  }

  async getResults(taskId, groupId = null, postId = null) {
    let whereClause = { taskId };
    if (postId) {
      whereClause.id = postId;
    }

    let postInclude = {
      model: Comment,
      as: 'comments', // Предполагая ассоциацию Post.hasMany(Comment, {as: 'comments'})
    };

    if (groupId) {
      // Предполагая поле groupId в Post
      whereClause.groupId = groupId;
    }

    const posts = await this.Post.findAll({
      where: whereClause,
      include: [postInclude],
    });

    const totalComments = posts.reduce((sum, post) => sum + (post.comments?.length || 0), 0);

    return {
      posts,
      totalComments,
    };
  }
}

module.exports = new DBRepo();