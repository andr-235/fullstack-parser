import { readdirSync } from 'fs';
import { basename as _basename, join } from 'path';
import Sequelize from 'sequelize';
const basename = _basename(__filename);
const db = {};

let sequelize;
let DataTypes;

export default (sequelizeInstance, dataTypesInstance) => {
  sequelize = sequelizeInstance;
  DataTypes = dataTypesInstance;

  readdirSync(__dirname)
    .filter(file => {
      return (
        file.indexOf('.') !== 0 &&
        file !== basename &&
        file.slice(-3) === '.js' &&
        file.indexOf('.test.js') === -1
      );
    })
    .forEach(file => {
      const model = require(join(__dirname, file))(sequelize, DataTypes);
      db[model.name] = model;
    });

  // Associations
  db.Task.hasMany(db.Post, { foreignKey: 'taskId' });
  db.Post.belongsTo(db.Task, { foreignKey: 'taskId' });
  db.Post.hasMany(db.Comment, { foreignKey: 'postId' });
  db.Comment.belongsTo(db.Post, { foreignKey: 'postId' });

  Object.keys(db).forEach(modelName => {
    if (db[modelName].associate) {
      db[modelName].associate(db);
    }
  });

  db.sequelize = sequelize;
  db.Sequelize = Sequelize;

  return db;
};