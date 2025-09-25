const { DataTypes } = require('sequelize');
const sequelize = require('../config/db.js');

const Comment = sequelize.define('Comment', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  vk_comment_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    unique: true
  },
  post_vk_id: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  owner_id: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  author_id: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  author_name: {
    type: DataTypes.STRING(255),
    allowNull: false
  },
  text: {
    type: DataTypes.TEXT,
    allowNull: false,
    defaultValue: ''
  },
  date: {
    type: DataTypes.DATE,
    allowNull: false
  },
  likes: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0
  },
  // Legacy fields for backward compatibility
  userId: {
    type: DataTypes.INTEGER,
    allowNull: true
  },
  postId: {
    type: DataTypes.INTEGER,
    allowNull: true
  }
}, {
  tableName: 'comments',
  timestamps: true
});

module.exports = Comment;