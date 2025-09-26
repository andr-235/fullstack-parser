import {
  Table,
  Column,
  Model,
  DataType,
  PrimaryKey,
  AutoIncrement,
  CreatedAt,
  UpdatedAt,
  BelongsTo,
  HasMany,
  ForeignKey,
  Index,
  Unique
} from 'sequelize-typescript';
import { Optional } from 'sequelize';
// Импорты для типов будут добавлены после инициализации всех моделей

// Интерфейсы для атрибутов Post
export interface PostAttributes {
  id: number;
  vk_post_id: number;
  owner_id: number;
  group_id: number;
  text: string;
  date: Date;
  likes: number;
  taskId: number;
  // Legacy fields for backward compatibility
  ownerId: number | null;
  groupId: number | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface PostCreationAttributes extends Optional<PostAttributes,
  'id' | 'likes' | 'ownerId' | 'groupId' | 'createdAt' | 'updatedAt'
> {}

@Table({
  tableName: 'posts',
  timestamps: true,
  indexes: [
    { fields: ['vk_post_id'], unique: true },
    { fields: ['owner_id'] },
    { fields: ['group_id'] },
    { fields: ['taskId'] },
    { fields: ['date'] },
    { fields: ['likes'] }
  ],
  comment: 'Таблица постов из VK'
})
export class Post extends Model<PostAttributes, PostCreationAttributes> {
  @PrimaryKey
  @AutoIncrement
  @Column(DataType.INTEGER)
  declare id: number;

  @Unique
  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    comment: 'ID поста в VK'
  })
  declare vk_post_id: number;

  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    comment: 'ID владельца поста в VK'
  })
  declare owner_id: number;

  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    comment: 'ID группы в VK'
  })
  declare group_id: number;

  @Column({
    type: DataType.TEXT,
    allowNull: false,
    defaultValue: '',
    comment: 'Текст поста'
  })
  declare text: string;

  @Column({
    type: DataType.DATE,
    allowNull: false,
    comment: 'Дата создания поста в VK'
  })
  declare date: Date;

  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    defaultValue: 0,
    comment: 'Количество лайков'
  })
  declare likes: number;

  // @ForeignKey(() => Task) - будет определена в index.ts
  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    comment: 'ID задачи, в рамках которой был получен пост'
  })
  declare taskId: number;

  // Legacy fields for backward compatibility
  @Column({
    type: DataType.INTEGER,
    allowNull: true,
    comment: 'Legacy поле для совместимости'
  })
  declare ownerId: number | null;

  @Column({
    type: DataType.INTEGER,
    allowNull: true,
    comment: 'Legacy поле для совместимости'
  })
  declare groupId: number | null;

  @CreatedAt
  declare createdAt: Date;

  @UpdatedAt
  declare updatedAt: Date;

  // Связи с другими моделями будут определены в index.ts
  declare task?: any;
  declare comments?: any[];

  // Статические методы для удобных запросов
  static findByVkId(vk_post_id: number) {
    return this.findOne({
      where: { vk_post_id }
    });
  }

  static findByTask(taskId: number) {
    return this.findAll({
      where: { taskId },
      order: [['date', 'DESC']]
    });
  }

  static findByGroup(group_id: number) {
    return this.findAll({
      where: { group_id },
      order: [['date', 'DESC']]
    });
  }

  static findPopular(minLikes = 10) {
    return this.findAll({
      where: {
        likes: {
          [require('sequelize').Op.gte]: minLikes
        }
      },
      order: [['likes', 'DESC']]
    });
  }

  // Методы экземпляра
  async getCommentsCount(): Promise<number> {
    // Будет реализовано после инициализации всех моделей
    return 0;
  }

  async updateLikesCount(likes: number): Promise<Post> {
    this.likes = Math.max(0, likes);
    return this.save({ fields: ['likes'] });
  }
}