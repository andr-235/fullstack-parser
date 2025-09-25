const { DataTypes } = require('sequelize');
const sequelize = require('../config/db.js');

const Post = sequelize.define('Post', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  vk_post_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    unique: true
  },
  owner_id: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  group_id: {
    type: DataTypes.INTEGER,
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
  taskId: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  // Legacy field for backward compatibility
  ownerId: {
    type: DataTypes.INTEGER,
    allowNull: true
  },
  groupId: {
    type: DataTypes.INTEGER,
    allowNull: true
  }
}, {
  tableName: 'posts',
  timestamps: true
});

module.exports = Post;