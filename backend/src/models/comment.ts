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
  ForeignKey,
  Index,
  Unique
} from 'sequelize-typescript';
import { Optional } from 'sequelize';
import { Post } from './post';

// Интерфейсы для атрибутов Comment
export interface CommentAttributes {
  id: number;
  vk_comment_id: number;
  post_vk_id: number;
  owner_id: number;
  author_id: number;
  author_name: string;
  text: string;
  date: Date;
  likes: number;
  // Legacy fields for backward compatibility
  userId: number | null;
  postId: number | null;
  post_id?: number; // Foreign key for Post relationship
  createdAt: Date;
  updatedAt: Date;
}

export interface CommentCreationAttributes extends Optional<CommentAttributes,
  'id' | 'likes' | 'userId' | 'postId' | 'post_id' | 'createdAt' | 'updatedAt'
> {}

@Table({
  tableName: 'comments',
  timestamps: true,
  indexes: [
    { fields: ['vk_comment_id'], unique: true },
    { fields: ['post_vk_id'] },
    { fields: ['author_id'] },
    { fields: ['owner_id'] },
    { fields: ['date'] },
    { fields: ['likes'] },
    { fields: ['post_id'] }
  ],
  comment: 'Таблица комментариев из VK'
})
export class Comment extends Model<CommentAttributes, CommentCreationAttributes> {
  @PrimaryKey
  @AutoIncrement
  @Column(DataType.INTEGER)
  declare id: number;

  @Unique
  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    comment: 'ID комментария в VK'
  })
  declare vk_comment_id: number;

  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    comment: 'VK ID поста, к которому относится комментарий'
  })
  declare post_vk_id: number;

  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    comment: 'ID владельца поста в VK'
  })
  declare owner_id: number;

  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    comment: 'ID автора комментария в VK'
  })
  declare author_id: number;

  @Column({
    type: DataType.STRING(255),
    allowNull: false,
    comment: 'Имя автора комментария'
  })
  declare author_name: string;

  @Column({
    type: DataType.TEXT,
    allowNull: false,
    defaultValue: '',
    comment: 'Текст комментария'
  })
  declare text: string;

  @Column({
    type: DataType.DATE,
    allowNull: false,
    comment: 'Дата создания комментария в VK'
  })
  declare date: Date;

  @Column({
    type: DataType.INTEGER,
    allowNull: false,
    defaultValue: 0,
    comment: 'Количество лайков'
  })
  declare likes: number;

  @ForeignKey(() => Post)
  @Column({
    type: DataType.INTEGER,
    allowNull: true,
    comment: 'ID поста в нашей системе'
  })
  declare post_id?: number;

  // Legacy fields for backward compatibility
  @Column({
    type: DataType.INTEGER,
    allowNull: true,
    comment: 'Legacy поле для совместимости'
  })
  declare userId: number | null;

  @Column({
    type: DataType.INTEGER,
    allowNull: true,
    comment: 'Legacy поле для совместимости'
  })
  declare postId: number | null;

  @CreatedAt
  declare createdAt: Date;

  @UpdatedAt
  declare updatedAt: Date;

  // Связи с другими моделями
  @BelongsTo(() => Post, {
    foreignKey: 'post_id',
    targetKey: 'id',
    onDelete: 'CASCADE',
    onUpdate: 'CASCADE'
  })
  declare post?: Post;

  // Статические методы для удобных запросов
  static findByVkId(vk_comment_id: number) {
    return this.findOne({
      where: { vk_comment_id }
    });
  }

  static findByPost(post_vk_id: number) {
    return this.findAll({
      where: { post_vk_id },
      order: [['date', 'ASC']]
    });
  }

  static findByAuthor(author_id: number) {
    return this.findAll({
      where: { author_id },
      order: [['date', 'DESC']]
    });
  }

  static findPopular(minLikes = 5) {
    return this.findAll({
      where: {
        likes: {
          [require('sequelize').Op.gte]: minLikes
        }
      },
      order: [['likes', 'DESC']]
    });
  }

  static findByDateRange(startDate: Date, endDate: Date) {
    return this.findAll({
      where: {
        date: {
          [require('sequelize').Op.between]: [startDate, endDate]
        }
      },
      order: [['date', 'DESC']]
    });
  }

  // Методы экземпляра
  async updateLikesCount(likes: number): Promise<Comment> {
    this.likes = Math.max(0, likes);
    return this.save({ fields: ['likes'] });
  }

  isRecentComment(hours = 24): boolean {
    const hoursAgo = new Date(Date.now() - hours * 60 * 60 * 1000);
    return this.date > hoursAgo;
  }

  getTextLength(): number {
    return this.text.length;
  }

  hasText(): boolean {
    return this.text.trim().length > 0;
  }
}