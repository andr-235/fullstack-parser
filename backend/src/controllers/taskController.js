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
  groups: Joi.array().items(
    Joi.object({
      id: Joi.alternatives().try(
        Joi.number().integer().positive(),
        Joi.string().pattern(/^\d+$/).custom((value) => parseInt(value))
      ).required(),
      name: Joi.string().required()
    })
  ).min(1).required()
});

/**
 * Создает задачу на сбор комментариев из VK.
 * @param {Object} req - HTTP-запрос
 * @param {Object} res - HTTP-ответ
 * @returns {Promise<void>}
 */
const createTask = async (req, res) => {
  const requestId = req.id;
  try {
    logger.info('Processing createTask request', {
      ownerId: req.body.ownerId,
      postId: req.body.postId,
      id: requestId
    });

    const { error, value } = taskSchema.validate(req.body);
    if (error) {
      logger.warn('Validation error in createTask', {
        details: error.details[0].message,
        id: requestId
      });
      return res.status(400).json({ error: error.details[0].message });
    }
    const { ownerId, postId, token } = value;
    const { taskId } = await taskService.createTask({ ownerId, postId, token });
    logger.info('Task created successfully', { taskId, status: 'created', id: requestId });
    res.status(201).json({ taskId, status: 'created' });
  } catch (err) {
    if (err.name === 'ValidationError') {
      logger.warn('Validation error in createTask', {
        message: err.message,
        id: requestId
      });
      return res.status(400).json({ error: err.message });
    }
    logger.error('Error in createTask', {
      error: err.stack,
      id: requestId
    });
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
  const requestId = req.id;
  try {
    logger.info('Processing createVkCollectTask request', {
      groupsCount: req.body.groups?.length,
      id: requestId
    });

    const { error, value } = vkCollectSchema.validate(req.body);
    if (error) {
      logger.warn('Validation error in createVkCollectTask', {
        details: error.details[0].message,
        id: requestId
      });
      return res.status(400).json({ error: error.details[0].message });
    }

    const { groups } = value;

    // Нормализуем группы - убираем дубли и приводим к нужному формату
    const uniqueGroups = [];
    const seenIds = new Set();

    for (const group of groups) {
      const groupId = parseInt(group.id);
      if (!seenIds.has(groupId)) {
        seenIds.add(groupId);
        uniqueGroups.push({
          id: groupId,
          name: group.name.trim()
        });
      }
    }

    // Create task in database
    const { taskId } = await taskService.createTask({
      groups: uniqueGroups,
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

    logger.info('VK collect task created and queued', { taskId, groupsCount: groups.length, id: requestId });
    res.status(201).json({ taskId, status: 'created' });

  } catch (err) {
    logger.error('Error in createVkCollectTask', {
      error: err.stack,
      id: requestId
    });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// POST /api/collect/:taskId - Start collect
const postCollect = async (req, res) => {
  const requestId = req.id;
  try {
    const taskId = req.params.taskId;
    logger.info('Processing postCollect request', { taskId, id: requestId });

    const task = await taskService.getTaskById(taskId);
    if (!task) {
      logger.warn('Task not found in postCollect', { taskId, id: requestId });
      return res.status(404).json({ error: 'Task not found' });
    }
    const { status, startedAt } = await taskService.startCollect(taskId);
    logger.info('Collect started', { taskId, status, startedAt, id: requestId });
    res.status(202).json({ taskId, status: 'pending', startedAt });
  } catch (err) {
    if (err.message.includes('rate limit')) {
      logger.warn('Rate limit in postCollect', { taskId: req.params.taskId, id: requestId });
      return res.status(429).json({ error: 'Rate limit exceeded' });
    }
    if (err.name === 'ValidationError') {
      logger.warn('Validation error in postCollect', { message: err.message, id: requestId });
      return res.status(400).json({ error: err.message });
    }
    logger.error('Error in postCollect', {
      taskId: req.params.taskId,
      error: err.stack,
      id: requestId
    });
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

/**
 * Получает список задач с пагинацией и фильтрами.
 * @param {Object} req - HTTP-запрос с query params: page, limit, status?, type?
 * @param {Object} res - HTTP-ответ
 * @returns {Promise<void>}
 */
const getTasks = async (req, res) => {
  const requestId = req.id;
  try {
    logger.info('Processing getTasks request', {
      page: req.query.page,
      limit: req.query.limit,
      status: req.query.status,
      type: req.query.type,
      id: requestId
    });

    // Validation schema for query params
    const querySchema = Joi.object({
      page: Joi.number().integer().min(1).default(1),
      limit: Joi.number().integer().min(1).max(100).default(10),
      status: Joi.string().valid('pending', 'processing', 'completed', 'failed').allow(null),
      type: Joi.string().valid('fetch_comments', 'process_groups', 'analyze_posts').allow(null)
    });

    const { error, value } = querySchema.validate(req.query);
    if (error) {
      logger.warn('Validation error in getTasks', {
        details: error.details[0].message,
        id: requestId
      });
      return res.status(400).json({ error: error.details[0].message });
    }

    const { page, limit, status, type } = value;
    const { tasks, total } = await taskService.listTasks(page, limit, status, type);

    logger.info('Tasks listed successfully', {
      page,
      limit,
      status,
      type,
      total,
      id: requestId
    });

    res.json({
      tasks,
      total,
      page,
      limit
    });
  } catch (err) {
    if (err.name === 'ValidationError') {
      logger.warn('Validation error in getTasks', {
        message: err.message,
        id: requestId
      });
      return res.status(400).json({ error: err.message });
    }
    logger.error('Error in getTasks', {
      page: req.query.page,
      limit: req.query.limit,
      status: req.query.status,
      type: req.query.type,
      error: err.message,
      id: requestId
    });
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