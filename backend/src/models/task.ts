import {
  Table,
  Column,
  Model,
  DataType,
  PrimaryKey,
  AutoIncrement,
  CreatedAt,
  UpdatedAt,
  BeforeUpdate,
  HasMany,
  Index
} from 'sequelize-typescript';
import { Optional } from 'sequelize';
import { TaskStatus, TaskType } from '../types/task';

// Интерфейсы для атрибутов Task
export interface TaskAttributes {
  id: number;
  status: TaskStatus;
  type: TaskType;
  priority: number;
  progress: number;
  groups: Array<{ id: number; name: string }> | null;
  metrics: Record<string, any> | null;
  parameters: Record<string, any> | null;
  result: Record<string, any> | null;
  error: string | null;
  executionTime: number | null;
  startedAt: Date | null;
  finishedAt: Date | null;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface TaskCreationAttributes extends Optional<TaskAttributes,
  'id' | 'status' | 'priority' | 'progress' | 'groups' | 'metrics' | 'parameters' |
  'result' | 'error' | 'executionTime' | 'startedAt' | 'finishedAt' | 'createdBy' |
  'createdAt' | 'updatedAt'
> {}

@Table({
  tableName: 'tasks',
  timestamps: true,
  indexes: [
    { fields: ['status'] },
    { fields: ['type'] },
    { fields: ['createdAt'] },
    { fields: ['status', 'priority'], name: 'task_status_priority_idx' },
    { fields: ['type', 'status'], name: 'task_type_status_idx' }
  ],
  comment: 'Таблица задач для асинхронной обработки'
})
export class Task extends Model<TaskAttributes, TaskCreationAttributes> {
  @PrimaryKey
  @AutoIncrement
  @Column(DataType.INTEGER)
  declare id: number;

  @Column({
    type: DataType.ENUM('pending', 'processing', 'completed', 'failed'),
    allowNull: false,
    defaultValue: 'pending',
    validate: {
      isIn: {
        args: [['pending', 'processing', 'completed', 'failed']],
        msg: 'Status должен быть одним из: pending, processing, completed, failed'
      }
    }
  })
  declare status: TaskStatus;

  @Column({
    type: DataType.ENUM('fetch_comments', 'process_groups', 'analyze_posts'),
    allowNull: false,
    defaultValue: 'fetch_comments',
    validate: {
      isIn: {
        args: [['fetch_comments', 'process_groups', 'analyze_posts']],
        msg: 'Тип задачи должен быть одним из: fetch_comments, process_groups, analyze_posts'
      }
    }
  })
  declare type: TaskType;

  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    defaultValue: 0,
    validate: {
      min: 0,
      max: 10
    },
    comment: 'Приоритет задачи от 0 до 10'
  })
  declare priority: number;

  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    defaultValue: 0,
    validate: {
      min: 0,
      max: 100
    },
    comment: 'Прогресс выполнения задачи в процентах'
  })
  declare progress: number;

  @Column({
    type: DataType.JSONB,
    allowNull: true,
    defaultValue: null,
    validate: {
      isValidGroups(value: any) {
        if (value !== null && (!Array.isArray(value) || !value.every(item =>
          typeof item === 'object' && item.id && item.name
        ))) {
          throw new Error('Groups должно быть массивом объектов с полями id и name');
        }
      }
    },
    comment: 'Массив групп для обработки'
  })
  declare groups: Array<{ id: number; name: string }> | null;

  @Column({
    type: DataType.JSONB,
    allowNull: true,
    defaultValue: null,
    validate: {
      isValidMetrics(value: any) {
        if (value !== null && typeof value !== 'object') {
          throw new Error('Metrics должно быть JSON объектом');
        }
      }
    },
    comment: 'Метрики и аналитические данные'
  })
  declare metrics: Record<string, any> | null;

  @Column({
    type: DataType.JSONB,
    allowNull: true,
    defaultValue: null,
    comment: 'Параметры конфигурации для выполнения задачи'
  })
  declare parameters: Record<string, any> | null;

  @Column({
    type: DataType.JSONB,
    allowNull: true,
    defaultValue: null,
    comment: 'Результат выполнения задачи'
  })
  declare result: Record<string, any> | null;

  @Column({
    type: DataType.TEXT,
    allowNull: true,
    defaultValue: null,
    comment: 'Ошибки при выполнении'
  })
  declare error: string | null;

  @Column({
    type: DataType.INTEGER,
    allowNull: true,
    defaultValue: null,
    comment: 'Время выполнения задачи в миллисекундах'
  })
  declare executionTime: number | null;

  @Column({
    type: DataType.DATE,
    allowNull: true,
    defaultValue: null,
    comment: 'Время начала выполнения задачи'
  })
  declare startedAt: Date | null;

  @Column({
    type: DataType.DATE,
    allowNull: true,
    defaultValue: null,
    comment: 'Время окончания выполнения задачи'
  })
  declare finishedAt: Date | null;

  @Column({
    type: DataType.STRING(100),
    allowNull: false,
    defaultValue: 'system',
    comment: 'Идентификатор пользователя или системы, создавшего задачу'
  })
  declare createdBy: string;

  @CreatedAt
  declare createdAt: Date;

  @UpdatedAt
  declare updatedAt: Date;

  // Связи с другими моделями будут определены в index.ts
  declare posts?: any[];
  declare taskGroups?: any[];

  // Хуки для автоматического вычисления времени выполнения
  @BeforeUpdate
  static updateTimestamps(instance: Task): void {
    if (instance.changed('status')) {
      if (instance.status === 'processing' && !instance.startedAt) {
        instance.startedAt = new Date();
      }
      if (['completed', 'failed'].includes(instance.status) && !instance.finishedAt) {
        instance.finishedAt = new Date();
        if (instance.startedAt) {
          instance.executionTime = instance.finishedAt.getTime() - instance.startedAt.getTime();
        }
      }
    }
  }

  // Методы экземпляра для удобства работы с задачами
  async markAsProcessing(): Promise<Task> {
    this.status = 'processing';
    this.startedAt = new Date();
    return this.save();
  }

  async markAsCompleted(result: Record<string, any> | null = null): Promise<Task> {
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
  }

  async markAsFailed(error: Error | string): Promise<Task> {
    this.status = 'failed';
    this.finishedAt = new Date();
    this.error = typeof error === 'string' ? error : error.message || error.toString();
    if (this.startedAt) {
      this.executionTime = this.finishedAt.getTime() - this.startedAt.getTime();
    }
    return this.save();
  }

  async updateProgress(progress: number): Promise<Task> {
    this.progress = Math.max(0, Math.min(100, progress));
    return this.save({ fields: ['progress'] });
  }

  // Статические методы для удобных запросов
  static findPending() {
    return this.findAll({
      where: { status: 'pending' },
      order: [['priority', 'DESC'], ['createdAt', 'ASC']]
    });
  }

  static findProcessing() {
    return this.findAll({
      where: { status: 'processing' },
      order: [['startedAt', 'ASC']]
    });
  }

  static findByType(type: TaskType) {
    return this.findAll({
      where: { type },
      order: [['createdAt', 'DESC']]
    });
  }
}