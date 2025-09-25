const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(process.env.DB_URL, {
  logging: false
});

module.exports = sequelize;