import {
  Table,
  Column,
  Model,
  DataType,
  PrimaryKey,
  AutoIncrement,
  BelongsTo,
  ForeignKey,
  Index,
  Default
} from 'sequelize-typescript';
import { Optional } from 'sequelize';
import { Task } from './task';

// Типы для статуса группы
export type GroupStatus = 'valid' | 'invalid' | 'duplicate';

// Интерфейсы для атрибутов Group
export interface GroupAttributes {
  id: number;
  name: string | null;
  status: GroupStatus;
  taskId: string;
  uploadedAt: Date;
}

export interface GroupCreationAttributes extends Optional<GroupAttributes,
  'id' | 'status' | 'uploadedAt'
> {}

@Table({
  tableName: 'groups',
  timestamps: false,
  indexes: [
    { fields: ['taskId'] },
    { fields: ['status'] },
    { fields: ['uploadedAt'] },
    { fields: ['name'] }
  ],
  comment: 'Таблица групп для обработки'
})
export class Group extends Model<GroupAttributes, GroupCreationAttributes> {
  @PrimaryKey
  @AutoIncrement
  @Column({
    type: DataType.INTEGER,
    allowNull: false
  })
  declare id: number;

  @Column({
    type: DataType.STRING,
    allowNull: true,
    comment: 'Название группы'
  })
  declare name: string | null;

  @Default('valid')
  @Column({
    type: DataType.ENUM('valid', 'invalid', 'duplicate'),
    allowNull: false,
    comment: 'Статус группы'
  })
  declare status: GroupStatus;

  @ForeignKey(() => Task)
  @Column({
    type: DataType.UUID,
    allowNull: false,
    field: 'task_id',
    comment: 'ID задачи, к которой принадлежит группа'
  })
  declare taskId: string;

  @Default(DataType.NOW)
  @Column({
    type: DataType.DATE,
    allowNull: false,
    field: 'uploaded_at',
    comment: 'Время загрузки группы'
  })
  declare uploadedAt: Date;

  // Связи с другими моделями
  @BelongsTo(() => Task, {
    foreignKey: 'taskId',
    targetKey: 'id',
    onDelete: 'CASCADE',
    onUpdate: 'CASCADE'
  })
  declare task?: Task;

  // Статические методы для удобных запросов
  static findByTask(taskId: string) {
    return this.findAll({
      where: { taskId },
      order: [['uploadedAt', 'DESC']]
    });
  }

  static findByStatus(status: GroupStatus) {
    return this.findAll({
      where: { status },
      order: [['uploadedAt', 'DESC']]
    });
  }

  static findValid() {
    return this.findAll({
      where: { status: 'valid' },
      order: [['uploadedAt', 'DESC']]
    });
  }

  static findInvalid() {
    return this.findAll({
      where: { status: 'invalid' },
      order: [['uploadedAt', 'DESC']]
    });
  }

  static findDuplicates() {
    return this.findAll({
      where: { status: 'duplicate' },
      order: [['uploadedAt', 'DESC']]
    });
  }

  static async getTaskStatistics(taskId: string) {
    const groups = await this.findAll({
      where: { taskId },
      attributes: ['status']
    });

    return groups.reduce((stats, group) => {
      stats[group.status] = (stats[group.status] || 0) + 1;
      stats.total = (stats.total || 0) + 1;
      return stats;
    }, {} as Record<string, number>);
  }

  // Методы экземпляра
  async markAsValid(): Promise<Group> {
    this.status = 'valid';
    return this.save();
  }

  async markAsInvalid(): Promise<Group> {
    this.status = 'invalid';
    return this.save();
  }

  async markAsDuplicate(): Promise<Group> {
    this.status = 'duplicate';
    return this.save();
  }

  isValid(): boolean {
    return this.status === 'valid';
  }

  isInvalid(): boolean {
    return this.status === 'invalid';
  }

  isDuplicate(): boolean {
    return this.status === 'duplicate';
  }

  hasName(): boolean {
    return this.name !== null && this.name.trim().length > 0;
  }
}