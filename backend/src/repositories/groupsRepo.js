const Group = require('../models/group.js');
const logger = require('../utils/logger.js');

class GroupsRepository {
  constructor() {
    this.Group = Group;
  }
  
  /**
   * Создает группы в базе данных
   * @param {Array} groups - Массив групп для создания
   * @param {string} taskId - ID задачи
   * @returns {Array} Созданные группы
   */
  async createGroups(groups, taskId) {
    try {
      const groupsToCreate = groups.map(group => ({
        id: group.id,
        name: group.name,
        status: group.status || 'valid',
        taskId: taskId,
        uploadedAt: new Date()
      }));
      
      const createdGroups = await this.Group.bulkCreate(groupsToCreate, {
        ignoreDuplicates: true
      });
      
      logger.info('Groups created successfully', {
        taskId,
        count: createdGroups.length
      });
      
      return createdGroups;
    } catch (error) {
      logger.error('Failed to create groups', { taskId, error: error.message });
      throw new Error(`Failed to create groups: ${error.message}`);
    }
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
      const { limit = 20, offset = 0, status = 'all', search = '', sortBy = 'uploadedAt', sortOrder = 'desc' } = params;
      
      // Строим условия WHERE
      const where = {};
      
      // Фильтр по статусу
      if (status !== 'all') {
        where.status = status;
      }
      
      // Поиск по ID или названию
      if (search) {
        where[this.Group.sequelize.Op.or] = [
          { id: { [this.Group.sequelize.Op.like]: `%${search}%` } },
          { name: { [this.Group.sequelize.Op.like]: `%${search}%` } }
        ];
      }
      
      // Сортировка
      const order = [[sortBy, sortOrder.toUpperCase()]];
      
      const { count, rows } = await this.Group.findAndCountAll({
        where,
        limit: parseInt(limit),
        offset: parseInt(offset),
        order
      });
      
      return {
        groups: rows,
        total: count,
        pagination: {
          limit: parseInt(limit),
          offset: parseInt(offset),
          hasMore: offset + rows.length < count
        }
      };
    } catch (error) {
      logger.error('Failed to get groups', { params, error: error.message });
      throw new Error(`Failed to get groups: ${error.message}`);
    }
  }

  /**
   * Получает группы по ID задачи (для обратной совместимости)
   * @param {string} taskId - ID задачи
   * @param {number} limit - Лимит записей
   * @param {number} offset - Смещение
   * @returns {Object} Группы с пагинацией
   */
  async getGroupsByTaskId(taskId, limit = 20, offset = 0) {
    try {
      const { count, rows } = await this.Group.findAndCountAll({
        where: { taskId },
        limit: parseInt(limit),
        offset: parseInt(offset),
        order: [['uploadedAt', 'DESC']]
      });
      
      return {
        groups: rows,
        total: count,
        pagination: {
          limit: parseInt(limit),
          offset: parseInt(offset),
          hasMore: offset + rows.length < count
        }
      };
    } catch (error) {
      logger.error('Failed to get groups by task ID', { taskId, error: error.message });
      throw new Error(`Failed to get groups: ${error.message}`);
    }
  }
  
  /**
   * Получает группу по ID
   * @param {number} groupId - ID группы
   * @returns {Object|null} Группа или null
   */
  async getGroupById(groupId) {
    try {
      return await this.Group.findByPk(groupId);
    } catch (error) {
      logger.error('Failed to get group by ID', { groupId, error: error.message });
      throw new Error(`Failed to get group: ${error.message}`);
    }
  }
  
  /**
   * Обновляет статус группы
   * @param {number} groupId - ID группы
   * @param {string} status - Новый статус
   * @returns {Object} Обновленная группа
   */
  async updateGroupStatus(groupId, status) {
    try {
      const [affectedRows] = await this.Group.update(
        { status },
        { where: { id: groupId } }
      );
      
      if (affectedRows === 0) {
        throw new Error('Group not found');
      }
      
      return await this.getGroupById(groupId);
    } catch (error) {
      logger.error('Failed to update group status', { groupId, status, error: error.message });
      throw new Error(`Failed to update group status: ${error.message}`);
    }
  }
  
  /**
   * Удаляет группу по ID
   * @param {string} groupId - ID группы
   * @returns {boolean} Успешность удаления
   */
  async deleteGroup(groupId) {
    try {
      const deletedCount = await this.Group.destroy({
        where: { id: groupId }
      });
      
      logger.info('Group deleted successfully', { groupId, deleted: deletedCount > 0 });
      return deletedCount > 0;
    } catch (error) {
      logger.error('Failed to delete group', { groupId, error: error.message });
      throw new Error(`Failed to delete group: ${error.message}`);
    }
  }

  /**
   * Массовое удаление групп
   * @param {Array} groupIds - Массив ID групп
   * @returns {number} Количество удаленных групп
   */
  async deleteGroups(groupIds) {
    try {
      const deletedCount = await this.Group.destroy({
        where: { id: { [this.Group.sequelize.Op.in]: groupIds } }
      });
      
      logger.info('Groups deleted successfully', { groupIds, count: deletedCount });
      return deletedCount;
    } catch (error) {
      logger.error('Failed to delete groups', { groupIds, error: error.message });
      throw new Error(`Failed to delete groups: ${error.message}`);
    }
  }

  /**
   * Удаляет группы по ID задачи
   * @param {string} taskId - ID задачи
   * @returns {number} Количество удаленных групп
   */
  async deleteGroupsByTaskId(taskId) {
    try {
      const deletedCount = await this.Group.destroy({
        where: { taskId }
      });
      
      logger.info('Groups deleted successfully', { taskId, count: deletedCount });
      return deletedCount;
    } catch (error) {
      logger.error('Failed to delete groups by task ID', { taskId, error: error.message });
      throw new Error(`Failed to delete groups: ${error.message}`);
    }
  }
  
  /**
   * Получает статистику по группам
   * @param {string} taskId - ID задачи
   * @returns {Object} Статистика групп
   */
  async getGroupsStats(taskId) {
    try {
      const stats = await this.Group.findAll({
        where: { taskId },
        attributes: [
          'status',
          [this.Group.sequelize.fn('COUNT', this.Group.sequelize.col('id')), 'count']
        ],
        group: ['status'],
        raw: true
      });
      
      const result = {
        total: 0,
        valid: 0,
        invalid: 0,
        duplicate: 0
      };
      
      stats.forEach(stat => {
        const count = parseInt(stat.count);
        result.total += count;
        result[stat.status] = count;
      });
      
      return result;
    } catch (error) {
      logger.error('Failed to get groups stats', { taskId, error: error.message });
      throw new Error(`Failed to get groups stats: ${error.message}`);
    }
  }
  
  /**
   * Проверяет существование группы
   * @param {number} groupId - ID группы
   * @returns {boolean} Существует ли группа
   */
  async groupExists(groupId) {
    try {
      const count = await this.Group.count({
        where: { id: groupId }
      });
      
      return count > 0;
    } catch (error) {
      logger.error('Failed to check group existence', { groupId, error: error.message });
      return false;
    }
  }
}

module.exports = new GroupsRepository();
