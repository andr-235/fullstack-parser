import { DataTypes } from 'sequelize';

export default (sequelize) => {
  const Task = sequelize.define('Task', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    groups: {
      type: DataTypes.JSON,
      allowNull: false
    },
    status: {
      type: DataTypes.ENUM('pending', 'in_progress', 'completed', 'failed'),
      allowNull: false,
      defaultValue: 'pending'
    },
    metrics: {
      type: DataTypes.JSON,
      defaultValue: { posts: 0, comments: 0 }
    }
  }, {
    timestamps: true,
    indexes: []
  });

  return Task;
};