import winston from 'winston';
import { error as _error } from '../utils/logger';

import { Router } from 'express';
import { object, array, number } from 'joi';
import { createTask, getTaskById, startCollect, getTaskStatus, listTasks } from '../services/taskService';
import { getResults as _getResults } from '../services/vkService';

const router = Router();

// Validation schema for groups
const groupsSchema = object({
  groups: array().items(number().negative()).required()
});

// POST /api/groups - Create task
const postGroups = async (req, res) => {
  try {
    const { error, value } = groupsSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }
    const { taskId } = await createTask(value.groups);
    res.status(201).json({ taskId, status: 'created' });
  } catch (err) {
    if (err.name === 'ValidationError') {
      return res.status(400).json({ error: err.message });
    }
    _error('Error in postGroups', { error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// POST /api/collect/:taskId - Start collect
const postCollect = async (req, res) => {
  try {
    const taskId = req.params.taskId;
    const task = await getTaskById(taskId); // Assume getTaskById exists in taskService
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }
    const { status, startedAt } = await startCollect(taskId);
    res.status(202).json({ taskId, status: 'pending', startedAt });
  } catch (err) {
    if (err.message.includes('rate limit')) {
      return res.status(429).json({ error: 'Rate limit exceeded' });
    }
    if (err.name === 'ValidationError') {
      return res.status(400).json({ error: err.message });
    }
    _error('Error in postCollect', { taskId: req.params.taskId, error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// GET /api/tasks/:taskId - Get task status
const getTask = async (req, res) => {
  try {
    const { status, progress, errors } = await getTaskStatus(req.params.taskId);
    res.json({ status, progress, errors: errors || [] });
  } catch (err) {
    if (err.message.includes('not found')) {
      return res.status(404).json({ error: 'Task not found' });
    }
    _error('Error in getTask', { taskId: req.params.taskId, error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// GET /api/tasks - List tasks
const getTasks = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const { tasks, total } = await listTasks(page, limit);
    res.json({ tasks, total });
  } catch (err) {
    _error('Error in getTasks', { page: req.query.page, limit: req.query.limit, error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// GET /api/results/:taskId - Get results
const getResults = async (req, res) => {
  try {
    const taskId = req.params.taskId;
    const groupId = req.query.groupId ? parseInt(req.query.groupId) : undefined;
    const postId = req.query.postId ? parseInt(req.query.postId) : undefined;
    const results = await _getResults(taskId, groupId, postId);
    res.json(results);
  } catch (err) {
    if (err.message.includes('not found')) {
      return res.status(404).json({ error: 'Results not found' });
    }
    _error('Error in getResults', { taskId: req.params.taskId, groupId: req.query.groupId, postId: req.query.postId, error: err.message });
    res.status(500).json({ error: 'Internal server error' });
  }
};

// Routes
router.post('/groups', postGroups);
router.post('/collect/:taskId', postCollect);
router.get('/tasks/:taskId', getTask);
router.get('/tasks', getTasks);
router.get('/results/:taskId', getResults);

export default router;