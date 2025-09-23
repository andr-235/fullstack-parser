import logger from '../utils/logger.js';

import vkApi from '../repositories/vkApi.js';
import dbRepo from '../repositories/dbRepo.js';
import pLimit from 'p-limit';
import taskService from './taskService.js';

class VKService {
  constructor(vkApiInstance, dbRepoInstance) {
    this.vkApi = vkApiInstance || vkApi;
    this.dbRepo = dbRepoInstance || dbRepo;
  }

  async collectForTask(taskId, groups) {
    let totalPosts = 0;
    let totalComments = 0;
    const errors = [];
    const limit = pLimit(5); // max 5 parallel VK requests

    try {
      await this.dbRepo.updateTask(taskId, {
        status: 'in_progress'
      });

      const promises = groups.map(groupId =>
        limit(async () => {
          try {
            const posts = await this.vkApi.getPosts(-groupId, { count: 10 });
            let groupPosts = 0;
            let groupComments = 0;

            for (const post of posts.items || []) {
              const comments = await this.vkApi.getComments(-groupId, post.id);
              const mappedPost = {
                id: post.id,
                groupId: -groupId,
                text: post.text,
                date: new Date(post.date * 1000),
                likes: post.likes?.count || 0
              };
              await this.dbRepo.createPosts(taskId, [mappedPost]);
              groupPosts++;

              const mappedComments = (comments.items || []).map(comment => ({
                id: comment.id,
                postId: post.id,
                text: comment.text,
                authorId: comment.from_id,
                authorName: comment.from?.name || 'Unknown',
                date: new Date(comment.date * 1000),
                likes: comment.likes?.count || 0
              }));
              if (mappedComments.length > 0) {
                await this.dbRepo.createComments(post.id, mappedComments);
              }
              groupComments += mappedComments.length;
            }

            totalPosts += groupPosts;
            totalComments += groupComments;
          } catch (error) {
            logger.error('Error processing group', { groupId, error: error.message });
            errors.push(`Error processing group ${groupId}: ${error.message}`);
          }
        })
      );

      await Promise.allSettled(promises);

      const metrics = {
        posts: totalPosts,
        comments: totalComments,
        errors
      };

      if (errors.length > 0) {
        await this.dbRepo.updateTask(taskId, {
          status: 'failed',
          metrics
        });
      } else {
        await this.dbRepo.updateTask(taskId, {
          status: 'completed',
          metrics
        });
      }
    } catch (error) {
      logger.error('General error in collectForTask', { taskId, error: error.message });
      errors.push(`General error in collectForTask: ${error.message}`);
      await this.dbRepo.updateTask(taskId, {
        status: 'failed',
        metrics: { posts: totalPosts, comments: totalComments, errors }
      });
      throw error;
    }
  }
}

export default new VKService();