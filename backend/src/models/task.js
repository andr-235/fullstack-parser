const { DataTypes } = require('sequelize');
const sequelize = require('../config/db.js');

const Task = sequelize.define('Task', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  status: {
    type: DataTypes.ENUM('pending', 'processing', 'completed', 'failed'),
    allowNull: false,
    defaultValue: 'pending',
    validate: {
      isIn: {
        args: [['pending', 'processing', 'completed', 'failed']],
        msg: 'Status должен быть одним из: pending, processing, completed, failed'
      }
    }
  },
  type: {
    type: DataTypes.ENUM('fetch_comments', 'process_groups', 'analyze_posts'),
    allowNull: false,
    defaultValue: 'fetch_comments',
    validate: {
      isIn: {
        args: [['fetch_comments', 'process_groups', 'analyze_posts']],
        msg: 'Тип задачи должен быть одним из: fetch_comments, process_groups, analyze_posts'
      }
    }
  },
  priority: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0,
    validate: {
      min: 0,
      max: 10
    }
  },
  progress: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0,
    validate: {
      min: 0,
      max: 100
    }
  },
  // Используем JSONB для лучшей производительности с PostgreSQL
  groups: {
    type: DataTypes.JSONB,
    allowNull: true,
    defaultValue: null,
    validate: {
      isValidGroups(value) {
        if (value !== null && (!Array.isArray(value) || !value.every(item =>
          typeof item === 'object' && item.id && item.name
        ))) {
          throw new Error('Groups должно быть массивом объектов с полями id и name');
        }
      }
    }
  },
  // Используем JSONB для метрик и аналитических данных
  metrics: {
    type: DataTypes.JSONB,
    allowNull: true,
    defaultValue: null,
    validate: {
      isValidMetrics(value) {
        if (value !== null && typeof value !== 'object') {
          throw new Error('Metrics должно быть JSON объектом');
        }
      }
    }
  },
  // Дополнительные параметры задачи
  parameters: {
    type: DataTypes.JSONB,
    allowNull: true,
    defaultValue: null,
    comment: 'Параметры конфигурации для выполнения задачи'
  },
  // Результат выполнения задачи
  result: {
    type: DataTypes.JSONB,
    allowNull: true,
    defaultValue: null,
    comment: 'Результат выполнения задачи'
  },
  // Ошибки при выполнении
  error: {
    type: DataTypes.TEXT,
    allowNull: true,
    defaultValue: null
  },
  // Время выполнения задачи
  executionTime: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: null,
    comment: 'Время выполнения задачи в миллисекундах'
  },
  startedAt: {
    type: DataTypes.DATE,
    allowNull: true,
    defaultValue: null
  },
  finishedAt: {
    type: DataTypes.DATE,
    allowNull: true,
    defaultValue: null
  },
  // Идентификатор пользователя или системы, создавшего задачу
  createdBy: {
    type: DataTypes.STRING(100),
    allowNull: true,
    defaultValue: 'system'
  }
}, {
  tableName: 'tasks',
  timestamps: true,
  indexes: [
    {
      fields: ['status']
    },
    {
      fields: ['type']
    },
    {
      fields: ['createdAt']
    },
    {
      fields: ['status', 'priority'],
      name: 'task_status_priority_idx'
    },
    {
      fields: ['type', 'status'],
      name: 'task_type_status_idx'
    }
  ],
  // Хуки для автоматического вычисления времени выполнения
  hooks: {
    beforeUpdate: (task) => {
      if (task.changed('status')) {
        if (task.status === 'processing' && !task.startedAt) {
          task.startedAt = new Date();
        }
        if (['completed', 'failed'].includes(task.status) && !task.finishedAt) {
          task.finishedAt = new Date();
          if (task.startedAt) {
            task.executionTime = task.finishedAt.getTime() - task.startedAt.getTime();
          }
        }
      }
    }
  }
});

// Методы экземпляра для удобства работы с задачами
Task.prototype.markAsProcessing = function() {
  this.status = 'processing';
  this.startedAt = new Date();
  return this.save();
};

Task.prototype.markAsCompleted = function(result = null) {
  this.status = 'completed';
  this.finishedAt = new Date();
  this.progress = 100;
  if (result) {
    this.result = result;
  }
  if (this.startedAt) {
    this.executionTime = this.finishedAt.getTime() - this.startedAt.getTime();
  }
  return this.save();
};

Task.prototype.markAsFailed = function(error) {
  this.status = 'failed';
  this.finishedAt = new Date();
  this.error = error.message || error.toString();
  if (this.startedAt) {
    this.executionTime = this.finishedAt.getTime() - this.startedAt.getTime();
  }
  return this.save();
};

Task.prototype.updateProgress = function(progress) {
  this.progress = Math.max(0, Math.min(100, progress));
  return this.save(['progress']);
};

// Статические методы для удобных запросов
Task.findPending = function() {
  return this.findAll({
    where: { status: 'pending' },
    order: [['priority', 'DESC'], ['createdAt', 'ASC']]
  });
};

Task.findProcessing = function() {
  return this.findAll({
    where: { status: 'processing' },
    order: [['startedAt', 'ASC']]
  });
};

Task.findByType = function(type) {
  return this.findAll({
    where: { type },
    order: [['createdAt', 'DESC']]
  });
};

module.exports = Task;