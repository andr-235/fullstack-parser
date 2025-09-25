const sequelize = require('../config/db.js');
const Comment = require('./comment');
const Post = require('./post');
const Task = require('./task');

// Associations for legacy compatibility
Comment.belongsTo(Post, { foreignKey: 'postId' });
Post.hasMany(Comment, { foreignKey: 'postId', as: 'comments' });

// New associations using VK IDs (primary)
// Post.belongsTo(Comment, { foreignKey: 'post_vk_id', targetKey: 'vk_post_id' });

// Task associations
Post.belongsTo(Task, { foreignKey: 'taskId' });
Task.hasMany(Post, { foreignKey: 'taskId' });

module.exports = { sequelize, Comment, Post, Task };