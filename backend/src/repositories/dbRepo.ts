import logger from '../utils/logger';
import { sequelize, Task, Post, Comment } from '../models/index';
import {
  TaskAttributes,
  TaskCreationAttributes,
  PostAttributes,
  PostCreationAttributes,
  CommentAttributes,
  CommentCreationAttributes
} from '../models/index';

// Интерфейсы для запросов
interface ListTasksOptions {
  limit: number;
  offset: number;
  status?: string;
  type?: string;
}

interface ListTasksResult {
  tasks: Task[];
  total: number;
}

interface GetResultsResult {
  posts: Post[];
  totalComments: number;
}

interface TaskUpdateData {
  status?: string;
  progress?: number;
  error?: string;
  result?: Record<string, any>;
  finishedAt?: Date;
  [key: string]: any;
}

class DBRepo {
  private sequelize: typeof sequelize;
  private Task: typeof Task;
  private Post: typeof Post;
  private Comment: typeof Comment;

  constructor() {
    this.sequelize = sequelize;
    this.Task = Task;
    this.Post = Post;
    this.Comment = Comment;
  }

  /**
   * Создает новую задачу
   */
  async createTask(groups: Array<{ id: number; name: string }>): Promise<Task> {
    const task = await this.Task.create({
      type: 'fetch_comments',
      status: 'pending',
      groups: groups,
      progress: 0,
      priority: 0,
      createdBy: 'system'
    });
    return task;
  }

  /**
   * Получает задачу по ID
   */
  async getTaskById(taskId: number): Promise<Task> {
    const task = await this.Task.findByPk(taskId);
    if (!task) {
      throw new Error(`Task with id ${taskId} not found`);
    }
    return task;
  }

  /**
   * Обновляет задачу
   */
  async updateTask(taskId: number, updates: TaskUpdateData): Promise<Task> {
    const [updatedCount] = await this.Task.update(updates, {
      where: { id: taskId },
      returning: true,
    });

    if (updatedCount === 0) {
      logger.error('Failed to update task', { taskId, error: `Task with id ${taskId} not found` });
      throw new Error(`Task with id ${taskId} not found`);
    }

    const updatedTask = await this.Task.findByPk(taskId);
    if (!updatedTask) {
      throw new Error(`Task with id ${taskId} not found after update`);
    }
    return updatedTask;
  }

  /**
   * Создает посты для задачи
   */
  async createPosts(taskId: number, posts: Partial<PostCreationAttributes>[]): Promise<Post[]> {
    const taskPosts = posts.map(post => ({
      ...post,
      taskId,
    }));
    const createdPosts = await this.Post.bulkCreate(taskPosts as PostCreationAttributes[]);
    return createdPosts;
  }

  /**
   * Создает комментарии для поста
   */
  async createComments(postId: number, comments: Partial<CommentCreationAttributes>[]): Promise<Comment[]> {
    const postComments = comments.map(comment => ({
      ...comment,
      postId,
    }));
    const createdComments = await this.Comment.bulkCreate(postComments as CommentCreationAttributes[]);
    return createdComments;
  }

  /**
   * Создает или обновляет посты (upsert)
   */
  async upsertPosts(taskId: number, posts: Partial<PostCreationAttributes>[]): Promise<Post[]> {
    const taskPosts = posts.map(post => ({
      ...post,
      taskId,
    }));

    try {
      const createdPosts = await this.Post.bulkCreate(taskPosts as PostCreationAttributes[], {
        updateOnDuplicate: ['text', 'date', 'likes', 'owner_id', 'group_id', 'updatedAt'],
        ignoreDuplicates: false
      });
      return createdPosts;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to upsert posts', { taskId, error: errorMsg });
      throw new Error(`Failed to upsert posts: ${errorMsg}`);
    }
  }

  /**
   * Создает или обновляет комментарии (upsert)
   */
  async upsertComments(postVkId: number, comments: Partial<CommentCreationAttributes>[]): Promise<Comment[]> {
    try {
      // Найти пост по vk_post_id для связи с комментариями
      const post = await this.Post.findOne({ where: { vk_post_id: postVkId } });
      if (!post) {
        throw new Error(`Post with vk_post_id ${postVkId} not found`);
      }

      // Добавить postId к комментариям для корректной ассоциации
      const commentsWithPostId = comments.map(comment => ({
        ...comment,
        postId: post.id, // Связь через внутренний ID поста
        post_id: post.id  // Новая связь через post_id
      }));

      const createdComments = await this.Comment.bulkCreate(commentsWithPostId as CommentCreationAttributes[], {
        updateOnDuplicate: ['text', 'date', 'likes', 'author_id', 'author_name', 'updatedAt'],
        ignoreDuplicates: false
      });
      return createdComments;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to upsert comments', { postVkId, error: errorMsg });
      throw new Error(`Failed to upsert comments: ${errorMsg}`);
    }
  }

  /**
   * Получает список задач с пагинацией и опциональными фильтрами
   */
  async listTasks({ limit, offset, status, type }: ListTasksOptions): Promise<ListTasksResult> {
    const where: Record<string, any> = {};
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

  /**
   * Получает результаты задачи с постами и комментариями
   */
  async getResults(taskId: number, groupId: number | null = null, postId: number | null = null): Promise<GetResultsResult> {
    let whereClause: Record<string, any> = { taskId };

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

    const totalComments = posts.reduce((sum, post) => {
      const commentsCount = (post as any).comments?.length || 0;
      return sum + commentsCount;
    }, 0);

    return {
      posts,
      totalComments,
    };
  }

  /**
   * Получает статистику по задаче
   */
  async getTaskStats(taskId: number): Promise<{
    postsCount: number;
    commentsCount: number;
    avgLikesPerPost: number;
    avgCommentsPerPost: number;
  }> {
    const posts = await this.Post.findAll({
      where: { taskId },
      include: [{
        model: Comment,
        as: 'comments'
      }]
    });

    const postsCount = posts.length;
    const totalLikes = posts.reduce((sum, post) => sum + post.likes, 0);
    const totalComments = posts.reduce((sum, post) => {
      const commentsCount = (post as any).comments?.length || 0;
      return sum + commentsCount;
    }, 0);

    return {
      postsCount,
      commentsCount: totalComments,
      avgLikesPerPost: postsCount > 0 ? Math.round(totalLikes / postsCount * 100) / 100 : 0,
      avgCommentsPerPost: postsCount > 0 ? Math.round(totalComments / postsCount * 100) / 100 : 0
    };
  }

  /**
   * Удаляет данные задачи
   */
  async deleteTaskData(taskId: number): Promise<void> {
    try {
      // Удаляем комментарии для всех постов задачи
      await this.Comment.destroy({
        include: [{
          model: Post,
          where: { taskId }
        }]
      });

      // Удаляем посты задачи
      await this.Post.destroy({ where: { taskId } });

      logger.info('Task data deleted successfully', { taskId });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete task data', { taskId, error: errorMsg });
      throw new Error(`Failed to delete task data: ${errorMsg}`);
    }
  }
}

export default new DBRepo();