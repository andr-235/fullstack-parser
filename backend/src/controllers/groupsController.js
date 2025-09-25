const express = require('express');
const { upload, handleUploadError } = require('../middleware/upload.js');
const groupsService = require('../services/groupsService.js');
const logger = require('../utils/logger.js');

const router = express.Router();

/**
 * POST /api/groups/upload
 * Загрузка файла с группами
 */
router.post('/upload', upload, handleUploadError, async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'NO_FILE',
        message: 'No file uploaded'
      });
    }
    
    const encoding = req.body.encoding || 'utf-8';
    const result = await groupsService.uploadGroups(req.file.buffer, encoding);
    
    if (result.success) {
      res.status(200).json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    logger.error('Upload groups controller error', { error: error.message });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
    });
  }
});

/**
 * GET /api/groups/upload/:taskId/status
 * Получение статуса загрузки
 */
router.get('/upload/:taskId/status', async (req, res) => {
  try {
    const { taskId } = req.params;
    const result = groupsService.getUploadStatus(taskId);
    
    if (result.success) {
      res.status(200).json(result);
    } else {
      res.status(404).json(result);
    }
  } catch (error) {
    logger.error('Get upload status controller error', { 
      taskId: req.params.taskId, 
      error: error.message 
    });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
    });
  }
});

/**
 * GET /api/groups
 * Получение списка групп
 */
router.get('/', async (req, res) => {
  try {
    const { 
      page = 1, 
      limit = 20, 
      status = 'all', 
      search = '', 
      sortBy = 'uploadedAt', 
      sortOrder = 'desc' 
    } = req.query;
    
    const offset = (parseInt(page) - 1) * parseInt(limit);
    const result = await groupsService.getGroups({
      limit: parseInt(limit),
      offset,
      status,
      search,
      sortBy,
      sortOrder
    });
    
    if (result.success) {
      res.status(200).json(result.data);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    logger.error('Get groups controller error', { 
      query: req.query, 
      error: error.message 
    });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
    });
  }
});

/**
 * DELETE /api/groups/:groupId
 * Удаление группы
 */
router.delete('/:groupId', async (req, res) => {
  try {
    const { groupId } = req.params;
    const result = await groupsService.deleteGroup(groupId);
    
    if (result.success) {
      res.status(200).json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    logger.error('Delete group controller error', { 
      groupId: req.params.groupId, 
      error: error.message 
    });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
    });
  }
});

/**
 * DELETE /api/groups/batch
 * Массовое удаление групп
 */
router.delete('/batch', async (req, res) => {
  try {
    const { groupIds } = req.body;
    
    if (!groupIds || !Array.isArray(groupIds)) {
      return res.status(400).json({
        success: false,
        error: 'INVALID_GROUP_IDS',
        message: 'groupIds must be an array'
      });
    }
    
    const result = await groupsService.deleteGroups(groupIds);
    
    if (result.success) {
      res.status(200).json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    logger.error('Delete groups batch controller error', { 
      groupIds: req.body.groupIds, 
      error: error.message 
    });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
    });
  }
});

/**
 * GET /api/groups/:taskId/stats
 * Получение статистики по группам
 */
router.get('/:taskId/stats', async (req, res) => {
  try {
    const { taskId } = req.params;
    const result = await groupsService.getGroupsStats(taskId);
    
    if (result.success) {
      res.status(200).json(result.data);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    logger.error('Get groups stats controller error', { 
      taskId: req.params.taskId, 
      error: error.message 
    });
    res.status(500).json({
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'Internal server error'
    });
  }
});

module.exports = router;
