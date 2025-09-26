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
    let task = null;

    try {
      // Получаем задачу и переводим в статус processing
      task = await this.dbRepo.getTaskById(taskId);
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
          const result = await this.vkApi.getPosts(groupId);
          const posts = result?.posts || [];
          logger.info('Posts received for processing', { groupId, taskId, count: posts.length });

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

          // Update progress and metrics periodically for UI tracking
          const currentProgress = Math.min(80, Math.round((totalPosts / (normalizedGroups.length * 10)) * 80));
          await task.updateProgress(currentProgress);

          // Update metrics using new method
          task.metrics = {
            posts: totalPosts,
            comments: totalComments,
            errors: [...errors]
          };
          await task.save(['metrics']);

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

      // Determine final status and mark task as completed/failed
      if (errors.length > 0) {
        const errorMessage = errors.join('; ');
        await task.markAsFailed(new Error(errorMessage));
      } else {
        // Update final result and mark as completed
        const result = {
          totalGroups: normalizedGroups.length,
          processedPosts: totalPosts,
          processedComments: totalComments,
          completedAt: new Date().toISOString()
        };
        await task.markAsCompleted(result);
      }

      // Update final metrics
      task.metrics = finalMetrics;
      await task.save(['metrics']);

      logger.info('Task completed', {
        taskId,
        status: task.status,
        totalPosts,
        totalComments,
        errorsCount: errors.length
      });

    } catch (error) {
      logger.error('General error in collectForTask', { taskId, error: error.message });
      errors.push(`General error in collectForTask: ${error.message}`);

      if (task) {
        await task.markAsFailed(error);

        // Update error metrics
        task.metrics = { posts: totalPosts, comments: totalComments, errors };
        await task.save(['metrics']);
      }

      throw error;
    }
  }
}

module.exports = new VKService();