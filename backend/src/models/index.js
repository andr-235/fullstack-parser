const sequelize = require('../config/db.js');
const Comment = require('./comment');
const Post = require('./post');
const Task = require('./task');

// Associations
Comment.belongsTo(Post, { foreignKey: 'postId' });
Post.hasMany(Comment, { foreignKey: 'postId', as: 'comments' });
Post.belongsTo(Task, { foreignKey: 'taskId' });
Task.hasMany(Post, { foreignKey: 'taskId' });

module.exports = { sequelize, Comment, Post, Task };