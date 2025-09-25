const logger = require('../utils/logger.js');

const vkApi = require('../repositories/vkApi.js');
const dbRepo = require('../repositories/dbRepo.js');

class VKService {
  constructor(vkApiInstance, dbRepoInstance) {
    this.vkApi = vkApiInstance || vkApi;
    this.dbRepo = dbRepoInstance || dbRepo;
  }

  async getResults(taskId, groupId = null, postId = null) {
    return await this.dbRepo.getResults(taskId, groupId, postId);
  }

  async collectForTask(taskId, groups) {
    let totalPosts = 0;
    let totalComments = 0;
    const errors = [];

    try {
      // Получаем задачу и переводим в статус processing
      const task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        throw new Error(`Task with id ${taskId} not found`);
      }

      await task.markAsProcessing();

      // Convert groups to positive numbers if needed
      const normalizedGroups = groups.map(group => Math.abs(parseInt(group)));

      for (const groupId of normalizedGroups) {
        try {
          logger.info('Processing group', { groupId, taskId });

          // Get posts from VK API (already normalized)
          const { posts } = await this.vkApi.getPosts(groupId);

          // Take only first 10 posts as required
          const postsToProcess = posts.slice(0, 10);
          let groupPosts = 0;
          let groupComments = 0;

          if (postsToProcess.length > 0) {
            // Upsert posts
            await this.dbRepo.upsertPosts(taskId, postsToProcess);
            groupPosts = postsToProcess.length;

            // Process comments for each post
            for (const post of postsToProcess) {
              try {
                const { comments } = await this.vkApi.getComments(groupId, post.vk_post_id);

                if (comments.length > 0) {
                  await this.dbRepo.upsertComments(post.vk_post_id, comments);
                  groupComments += comments.length;
                }
              } catch (commentError) {
                logger.error('Error getting comments for post', {
                  groupId,
                  postId: post.vk_post_id,
                  error: commentError.message
                });
                errors.push(`Error getting comments for group ${groupId}, post ${post.vk_post_id}: ${commentError.message}`);
              }
            }
          }

          totalPosts += groupPosts;
          totalComments += groupComments;

          logger.info('Group processing completed', {
            groupId,
            taskId,
            groupPosts,
            groupComments
          });

          // Update progress periodically for UI tracking
          await this.dbRepo.updateTask(taskId, {
            metrics: {
              posts: totalPosts,
              comments: totalComments,
              errors: [...errors]
            }
          });

        } catch (error) {
          logger.error('Error processing group', { groupId, error: error.message });
          errors.push(`Error processing group ${groupId}: ${error.message}`);
        }
      }

      const finalMetrics = {
        posts: totalPosts,
        comments: totalComments,
        errors
      };

      // Determine final status
      const finalStatus = errors.length > 0 ? 'failed' : 'completed';

      await this.dbRepo.updateTask(taskId, {
        status: finalStatus,
        metrics: finalMetrics,
        finishedAt: new Date()
      });

      logger.info('Task completed', {
        taskId,
        status: finalStatus,
        totalPosts,
        totalComments,
        errorsCount: errors.length
      });

    } catch (error) {
      logger.error('General error in collectForTask', { taskId, error: error.message });
      errors.push(`General error in collectForTask: ${error.message}`);

      await this.dbRepo.updateTask(taskId, {
        status: 'failed',
        metrics: { posts: totalPosts, comments: totalComments, errors },
        finishedAt: new Date()
      });

      throw error;
    }
  }
}

module.exports = new VKService();