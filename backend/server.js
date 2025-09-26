const winston = require('winston');
const logger = require('./src/utils/logger.js');
const crypto = require('crypto');

const express = require('express');
const cors = require('cors'); // For CORS with frontend

const sequelize = require('./src/config/db.js');
const taskController = require('./src/controllers/taskController.js');
const groupsController = require('./src/controllers/groupsController.js');

const app = express();
const PORT = 3000;

// Middleware для логирования входящих запросов
app.use((req, res, next) => {
  const requestId = crypto.randomUUID();
  req.id = requestId;

  // Санитизация body: маскировка токенов
  const sanitizedBody = { ...req.body };
  if (sanitizedBody.token) {
    sanitizedBody.token = '***';
  }

  // Санитизация headers: удаление Authorization если есть
  const sanitizedHeaders = { ...req.headers };
  if (sanitizedHeaders.authorization) {
    sanitizedHeaders.authorization = '***';
  }

  logger.info('Incoming request', {
    method: req.method,
    url: req.url,
    body: sanitizedBody,
    headers: sanitizedHeaders,
    id: requestId
  });

  next();
});

// Middleware
app.use(express.json());
app.use(cors({
  origin: ['http://localhost:5173',  'http://frontend:5173', 'http://192.168.88.12:5173' ], // Allow Vue frontend local, external, Docker
  credentials: true
}));

// Basic route
app.get('/', (req, res) => {
  res.json({ message: 'Express VK Backend is running!' });
});

// Health check endpoint for deployment monitoring
app.get('/api/health', async (req, res) => {
  try {
    // Check database connection
    await sequelize.authenticate();

    res.status(200).json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        database: 'connected',
        server: 'running'
      },
      uptime: process.uptime()
    });
  } catch (error) {
    logger.error('Health check failed', { error: error.message });
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// Import routes
app.use('/api', taskController);
app.use('/api/groups', groupsController);

// Глобальный middleware для 404 ошибок
app.use((req, res, next) => {
  logger.warn('404 Not Found', {
    method: req.method,
    url: req.url,
    id: req.id
  });
  res.status(404).json({ error: 'Not Found' });
});

// Sync database and start server
sequelize.sync({ force: false }).then(() => {
  const server = app.listen(PORT, () => {
    logger.info(`Server running on port ${PORT}`);
  });
  
  // Export app for testing
  module.exports = app;
});