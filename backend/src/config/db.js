import { Sequelize } from 'sequelize';

const sequelize = new Sequelize(process.env.DB_URL, {
  dialect: 'postgres',
  logging: false
});

const models = require('../models').default(sequelize, Sequelize.DataTypes);

export default { sequelize, ...models };