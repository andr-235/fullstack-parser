import { Sequelize } from 'sequelize-typescript';
import sequelize from '../config/db.js';
import { Task } from './task.js';
import { Post } from './post.js';
import { Comment } from './comment.js';
import { Group } from './group.js';

// Инициализация моделей
sequelize.addModels([Task, Post, Comment, Group]);

// Настройка ассоциаций между моделями
Task.hasMany(Post, {
  foreignKey: 'taskId',
  sourceKey: 'id',
  as: 'posts'
});

Post.belongsTo(Task, {
  foreignKey: 'taskId',
  targetKey: 'id',
  as: 'task'
});

Task.hasMany(Group, {
  foreignKey: 'taskId',
  sourceKey: 'id',
  as: 'taskGroups'
});

Group.belongsTo(Task, {
  foreignKey: 'taskId',
  targetKey: 'id',
  as: 'task'
});

Post.hasMany(Comment, {
  foreignKey: 'post_id',
  sourceKey: 'id',
  as: 'comments'
});

Comment.belongsTo(Post, {
  foreignKey: 'post_id',
  targetKey: 'id',
  as: 'post'
});

// Legacy associations для совместимости
Comment.belongsTo(Post, {
  foreignKey: 'postId',
  targetKey: 'id',
  as: 'legacyPost'
});

Post.hasMany(Comment, {
  foreignKey: 'postId',
  sourceKey: 'id',
  as: 'legacyComments'
});

// Проверяем, что все модели зарегистрированы
const models = sequelize.models;

// Экспортируем модели и sequelize инстанс
export {
  sequelize,
  Task,
  Post,
  Comment,
  Group
};

// Экспортируем типы для использования в других модулях
export type {
  TaskAttributes,
  TaskCreationAttributes
} from './task.js';

export type {
  PostAttributes,
  PostCreationAttributes
} from './post.js';

export type {
  CommentAttributes,
  CommentCreationAttributes
} from './comment.js';

export type {
  GroupAttributes,
  GroupCreationAttributes,
  GroupStatus
} from './group.js';

// Дефолтный экспорт для совместимости
export default {
  sequelize,
  Task,
  Post,
  Comment,
  Group
};