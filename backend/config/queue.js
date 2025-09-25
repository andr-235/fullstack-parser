const logger = require('../src/utils/logger.js');

const { Queue, Worker } = require('bullmq');
const { Redis } = require('ioredis');
const taskService = require('../src/services/taskService.js');
const vkService = require('../src/services/vkService.js');

const redisConnection = new Redis(process.env.REDIS_URL);

const queue = new Queue('vk-collect', {
  connection: redisConnection
});

const worker = new Worker('vk-collect', async (job) => {
  const { taskId } = job.data;
  try {
    logger.info('Processing VK collect job', { taskId, jobId: job.id });

    const task = await taskService.getTaskById(taskId);
    if (!task) {
      throw new Error(`Task with id ${taskId} not found`);
    }

    const groups = JSON.parse(task.groups || '[]');
    if (groups.length === 0) {
      throw new Error('No groups specified for task');
    }

    await vkService.collectForTask(taskId, groups);

    logger.info('VK collect job completed successfully', { taskId, jobId: job.id });
  } catch (error) {
    logger.error('Queue job failed', {
      taskId,
      jobId: job.id,
      error: error.message,
      stack: error.stack
    });
    throw error;
  }
}, {
  connection: redisConnection,
  concurrency: 1,
  maxStalledCount: 1,
  stalledInterval: 30000,
  removeOnComplete: 100,
  removeOnFail: 50
});

module.exports = { queue, worker };