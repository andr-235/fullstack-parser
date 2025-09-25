const { DataTypes } = require('sequelize');
const sequelize = require('../config/db.js');

const Group = sequelize.define('Group', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
    allowNull: false
  },
  name: {
    type: DataTypes.STRING,
    allowNull: true
  },
  status: {
    type: DataTypes.ENUM('valid', 'invalid', 'duplicate'),
    defaultValue: 'valid'
  },
  taskId: {
    type: DataTypes.UUID,
    allowNull: false,
    field: 'task_id'
  },
  uploadedAt: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
    field: 'uploaded_at'
  }
}, {
  tableName: 'groups',
  timestamps: false
});

module.exports = Group;
