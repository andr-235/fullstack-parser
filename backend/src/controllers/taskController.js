const logger = require('../utils/logger.js');

const { Router } = require('express');
const Joi = require('joi');
const taskService = require('../services/taskService.js');
const vkService = require('../services/vkService.js');
const { queue } = require('../../config/queue.js');

const router = Router();

// Validation schema for task creation
const taskSchema = Joi.object({
  ownerId: Joi.number().integer().negative().required(),
  postId: Joi.number().integer().positive().required(),
  token: Joi.string().required()
});

// Validation schema for VK collect task creation
const vkCollectSchema = Joi.object({
  groups: Joi.array().items(Joi.number().integer().positive()).min(1).required()
});

/**
 * Создает задачу на сбор комментариев из VK.
 * @param {Object} req - HTTP-запрос
 * @param {Object} res - HTTP-ответ
 * @returns {Promise<void>}
 */
const createTask = async (req, res) => {
  try {
    const { error, value } = taskSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }
    const { ownerId, postId, token } = value;
    const { taskId } = await taskService.createTask({ ownerId, postId, token });
    res.status(201).json({ taskId, status: 'created' });
  } catch (err) {
    if (err.name === 'ValidationError') {
      return res.status(400).json({ error: err.message });
    }
    logger.error('Error in createTask', { error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

/**
 * Создает задачу на сбор постов и комментариев из VK групп через очередь BullMQ.
 * @param {Object} req - HTTP-запрос
 * @param {Object} res - HTTP-ответ
 * @returns {Promise<void>}
 */
const createVkCollectTask = async (req, res) => {
  try {
    const { error, value } = vkCollectSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const { groups } = value;

    // Create task in database
    const { taskId } = await taskService.createTask({
      groups,
      status: 'created',
      metrics: { posts: 0, comments: 0, errors: [] }
    });

    // Add job to BullMQ queue
    await queue.add('vk-collect', { taskId }, {
      delay: 1000, // Small delay to ensure task is saved
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 5000,
      },
      removeOnComplete: 100,
      removeOnFail: 50
    });

    logger.info('VK collect task created and queued', { taskId, groups });
    res.status(201).json({ taskId, status: 'created' });

  } catch (err) {
    logger.error('Error in createVkCollectTask', { error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// POST /api/collect/:taskId - Start collect
const postCollect = async (req, res) => {
  try {
    const taskId = req.params.taskId;
    const task = await taskService.getTaskById(taskId);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }
    const { status, startedAt } = await taskService.startCollect(taskId);
    res.status(202).json({ taskId, status: 'pending', startedAt });
  } catch (err) {
    if (err.message.includes('rate limit')) {
      return res.status(429).json({ error: 'Rate limit exceeded' });
    }
    if (err.name === 'ValidationError') {
      return res.status(400).json({ error: err.message });
    }
    logger.error('Error in postCollect', { taskId: req.params.taskId, error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// GET /api/tasks/:taskId - Get task status
const getTask = async (req, res) => {
  try {
    const { status, progress, errors } = await taskService.getTaskStatus(req.params.taskId);
    res.json({ status, progress, errors: errors || [] });
  } catch (err) {
    if (err.message.includes('not found')) {
      return res.status(404).json({ error: 'Task not found' });
    }
    logger.error('Error in getTask', { taskId: req.params.taskId, error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// GET /api/tasks - List tasks
const getTasks = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const { tasks, total } = await taskService.listTasks(page, limit);
    res.json({ tasks, total });
  } catch (err) {
    logger.error('Error in getTasks', { page: req.query.page, limit: req.query.limit, error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// GET /api/results/:taskId - Get results
const getResults = async (req, res) => {
  try {
    const taskId = req.params.taskId;
    const groupId = req.query.groupId ? parseInt(req.query.groupId) : undefined;
    const postId = req.query.postId ? parseInt(req.query.postId) : undefined;
    const results = await vkService.getResults(taskId, groupId, postId);
    res.json(results);
  } catch (err) {
    if (err.message.includes('not found')) {
      return res.status(404).json({ error: 'Results not found' });
    }
    logger.error('Error in getResults', { taskId: req.params.taskId, groupId: req.query.groupId, postId: req.query.postId, error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// Routes
router.post('/tasks', createTask);
router.post('/tasks/collect', createVkCollectTask);
router.post('/collect/:taskId', postCollect);
router.get('/tasks/:taskId', getTask);
router.get('/tasks', getTasks);
router.get('/results/:taskId', getResults);

module.exports = router;