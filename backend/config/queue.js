import logger from '../src/utils/logger.js';

import { Queue, Worker } from 'bullmq';
import { Redis } from 'ioredis';
import taskService from '../src/services/taskService.js';
import vkService from '../src/services/vkService.js';

const redisConnection = new Redis(process.env.REDIS_URL);

const queue = new Queue('vk-collect', {
  connection: redisConnection
});

const worker = new Worker('vk-collect', async (job) => {
  const { taskId } = job.data;
  try {
    const taskStatus = await taskService.getTaskStatus(taskId);
    await vkService.collectForTask(taskId, taskStatus.groups);
  } catch (error) {
    logger.error('Queue job failed', { taskId, error: error.message });
    throw error;
  }
}, {
  connection: redisConnection,
  concurrency: 1
});

export { queue, worker };