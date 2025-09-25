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

const syncAndStart = async () => {
  if (db.sequelize && typeof db.sequelize.sync === 'function') {
    await db.sequelize.sync({ force: false });
  } else {
    logger.warn('Skipping sequelize.sync: function not available');
  }

  app.listen(PORT, () => {
    logger.info(`Server running on port ${PORT}`);
  });
};

syncAndStart().catch((error) => {
  logger.error('Server failed to start', { error: error.message });
  process.exitCode = 1;
});

module.exports = app;