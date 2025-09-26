const { v4: uuidv4 } = require('uuid');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const FileParser = require('../utils/fileParser.js');
const VKValidator = require('../utils/vkValidator.js');
const groupsRepo = require('../repositories/groupsRepo.js');
const logger = require('../utils/logger.js');

class GroupsService {
  constructor() {
    this.vkValidator = null;
    this.uploadTasks = new Map(); // Хранение задач загрузки
  }
  
  /**
   * Инициализирует VK валидатор
   * @param {string} vkToken - Токен VK API
   */
  initializeVKValidator(vkToken) {
    this.vkValidator = new VKValidator(vkToken);
  }
  
  /**
   * Загружает группы из файла
   * @param {string|Buffer} filePath - Путь к файлу или Buffer с содержимым
   * @param {string} encoding - Кодировка файла
   * @returns {Object} Результат загрузки
   */
  async uploadGroups(filePath, encoding = 'utf-8') {
    const taskId = uuidv4();
    let tempPath = null;
    
    try {
      // Если это Buffer, сохраняем во временный файл
      let actualFilePath = filePath;
      if (Buffer.isBuffer(filePath)) {
        // Создаем папку для временных файлов
        const tempDir = path.join(os.tmpdir(), 'vk-uploads');
        await fs.mkdir(tempDir, { recursive: true });
        
        tempPath = path.join(tempDir, `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}.txt`);
        await fs.writeFile(tempPath, filePath);
        actualFilePath = tempPath;
      }
      
      // Валидация файла
      await FileParser.validateFile(actualFilePath);
      
      // Парсинг файла
      const parseResult = await FileParser.parseGroupsFile(actualFilePath, encoding);
      
      // Создаем задачу загрузки
      const uploadTask = {
        taskId,
        status: 'created',
        totalGroups: parseResult.groups.length,
        validGroups: 0,
        invalidGroups: 0,
        duplicates: 0,
        errors: parseResult.errors,
        createdAt: new Date(),
        startedAt: null,
        completedAt: null
      };
      
      this.uploadTasks.set(taskId, uploadTask);
      
      // Запускаем асинхронную обработку
      this.processGroupsAsync(taskId, parseResult.groups, parseResult.errors)
        .catch(error => {
          logger.error('Async processing failed', { taskId, error: error.message });
          this.updateTaskStatus(taskId, 'failed', { error: error.message });
        });
      
      // Удаляем временный файл если был создан
      if (tempPath) {
        await fs.unlink(tempPath);
      }
      
      return {
        success: true,
        data: {
          taskId,
          totalGroups: parseResult.groups.length,
          validGroups: 0, // Будет обновлено асинхронно
          invalidGroups: parseResult.errors.length,
          duplicates: 0
        }
      };
    } catch (error) {
      logger.error('Upload groups failed', { filePath, error: error.message });
      
      // Удаляем временный файл если был создан
      if (tempPath) {
        try {
          await fs.unlink(tempPath);
        } catch (unlinkError) {
          logger.warn('Failed to cleanup temp file', { tempPath, error: unlinkError.message });
        }
      }
      
      return {
        success: false,
        error: 'UPLOAD_ERROR',
        message: error.message
      };
    }
  }
  
  /**
   * Асинхронная обработка групп
   * @param {string} taskId - ID задачи
   * @param {Array} groups - Группы для обработки
   * @param {Array} parseErrors - Ошибки парсинга
   */
  async processGroupsAsync(taskId, groups, parseErrors) {
    try {
      this.updateTaskStatus(taskId, 'processing', { startedAt: new Date() });
      
      let validGroups = [];
      let invalidGroups = [];
      let duplicates = 0;
      
      // Если есть VK валидатор, валидируем группы
      if (this.vkValidator) {
        const validationResult = await this.vkValidator.validateGroups(groups);
        validGroups = validationResult.validGroups;
        invalidGroups = validationResult.invalidGroups;
      } else {
        // Без VK валидации все группы считаем валидными
        validGroups = groups.map(group => ({
          ...group,
          status: 'valid'
        }));
      }
      
      // Проверяем дубликаты в БД
      const groupsToSave = [];
      for (const group of validGroups) {
        if (group.id) {
          const exists = await groupsRepo.groupExists(group.id);
          if (exists) {
            duplicates++;
            invalidGroups.push({
              ...group,
              status: 'duplicate',
              error: 'Group already exists in database'
            });
          } else {
            groupsToSave.push(group);
          }
        } else {
          groupsToSave.push(group);
        }
      }
      
      // Сохраняем группы в БД
      if (groupsToSave.length > 0) {
        await groupsRepo.createGroups(groupsToSave, taskId);
      }
      
      // Обновляем статистику задачи
      this.updateTaskStatus(taskId, 'completed', {
        validGroups: groupsToSave.length,
        invalidGroups: invalidGroups.length + parseErrors.length,
        duplicates,
        completedAt: new Date()
      });
      
      logger.info('Groups processing completed', {
        taskId,
        validGroups: groupsToSave.length,
        invalidGroups: invalidGroups.length,
        duplicates
      });
    } catch (error) {
      logger.error('Groups processing failed', { taskId, error: error.message });
      this.updateTaskStatus(taskId, 'failed', { 
        error: error.message,
        completedAt: new Date()
      });
    }
  }
  
  /**
   * Получает статус задачи загрузки
   * @param {string} taskId - ID задачи
   * @returns {Object} Статус задачи
   */
  getUploadStatus(taskId) {
    const task = this.uploadTasks.get(taskId);
    if (!task) {
      return {
        success: false,
        error: 'TASK_NOT_FOUND',
        message: 'Upload task not found'
      };
    }
    
    const progress = task.totalGroups > 0 
      ? (task.validGroups + task.invalidGroups) / task.totalGroups * 100
      : 0;
    
    return {
      success: true,
      data: {
        status: task.status,
        progress: {
          processed: task.validGroups + task.invalidGroups,
          total: task.totalGroups,
          percentage: Math.round(progress * 100) / 100
        },
        errors: task.errors || []
      }
    };
  }
  
  /**
   * Получает группы с фильтрацией
   * @param {Object} params - Параметры фильтрации
   * @param {number} params.limit - Лимит записей
   * @param {number} params.offset - Смещение
   * @param {string} params.status - Фильтр по статусу
   * @param {string} params.search - Поиск по ID или названию
   * @param {string} params.sortBy - Поле сортировки
   * @param {string} params.sortOrder - Порядок сортировки
   * @returns {Object} Группы с пагинацией
   */
  async getGroups(params) {
    try {
      const result = await groupsRepo.getGroups(params);
      
      return {
        success: true,
        data: result
      };
    } catch (error) {
      logger.error('Get groups failed', { params, error: error.message });
      return {
        success: false,
        error: 'GET_GROUPS_ERROR',
        message: error.message
      };
    }
  }
  
  /**
   * Обновляет статус задачи
   * @param {string} taskId - ID задачи
   * @param {string} status - Новый статус
   * @param {Object} updates - Дополнительные обновления
   */
  updateTaskStatus(taskId, status, updates = {}) {
    const task = this.uploadTasks.get(taskId);
    if (task) {
      Object.assign(task, { status, ...updates });
      this.uploadTasks.set(taskId, task);
    }
  }
  
  
  /**
   * Удаляет группу
   * @param {string} groupId - ID группы
   * @returns {Object} Результат удаления
   */
  async deleteGroup(groupId) {
    try {
      const result = await groupsRepo.deleteGroup(groupId);
      
      if (result) {
        return {
          success: true,
          message: 'Group deleted successfully'
        };
      } else {
        return {
          success: false,
          error: 'GROUP_NOT_FOUND',
          message: 'Group not found'
        };
      }
    } catch (error) {
      logger.error('Delete group failed', { groupId, error: error.message });
      return {
        success: false,
        error: 'DELETE_GROUP_ERROR',
        message: error.message
      };
    }
  }

  /**
   * Массовое удаление групп
   * @param {Array} groupIds - Массив ID групп
   * @returns {Object} Результат удаления
   */
  async deleteGroups(groupIds) {
    try {
      const result = await groupsRepo.deleteGroups(groupIds);
      
      return {
        success: true,
        data: {
          deletedCount: result,
          message: `${result} groups deleted successfully`
        }
      };
    } catch (error) {
      logger.error('Delete groups failed', { groupIds, error: error.message });
      return {
        success: false,
        error: 'DELETE_GROUPS_ERROR',
        message: error.message
      };
    }
  }

  /**
   * Получает статистику по группам
   * @param {string} taskId - ID задачи
   * @returns {Object} Статистика
   */
  async getGroupsStats(taskId) {
    try {
      const stats = await groupsRepo.getGroupsStats(taskId);
      return {
        success: true,
        data: stats
      };
    } catch (error) {
      logger.error('Get groups stats failed', { taskId, error: error.message });
      return {
        success: false,
        error: 'GET_STATS_ERROR',
        message: error.message
      };
    }
  }
}

module.exports = new GroupsService();
