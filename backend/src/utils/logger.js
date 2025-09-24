import { createLogger, format as _format, transports as _transports } from 'winston';

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

export default logger;