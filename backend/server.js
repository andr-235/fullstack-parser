const winston = require('winston');
const logger = require('./src/utils/logger');

const express = require('express');
const cors = require('cors'); // For CORS with frontend

const app = express();
const PORT = 3000;

const db = require('./src/config/db');

// Middleware
app.use(express.json());
app.use(cors({
  origin: 'http://localhost:5173', // Allow Vue frontend
  credentials: true
}));

// Basic route
app.get('/', (req, res) => {
  res.json({ message: 'Express VK Backend is running!' });
});

// Import routes
app.use('/api', require('./src/controllers/taskController'));

db.sequelize.sync({ force: false }).then(() => {
  app.listen(PORT, () => {
    logger.info(`Server running on port ${PORT}`);
  });
});

module.exports = app;