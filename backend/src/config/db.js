const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(process.env.DATABASE_URL, {
  dialect: 'postgres',
  logging: false
});

const models = require('../models')(sequelize, Sequelize.DataTypes);

module.exports = { sequelize, ...models };