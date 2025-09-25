const { createLogger, format: _format, transports: _transports } = require('winston');

const logger = createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: _format.combine(
    _format.timestamp(),
    _format.json()
  ),
  transports: [
    new _transports.Console(),
    new _transports.File({ filename: 'logs/app.log' })
  ]
});

module.exports = logger;