/**
 * Winston logger instance for VK backend.
 * Methods: .info(msg, [meta]), .error(err, [meta]), .warn(msg, [meta]), .debug(msg, [meta]).
 */

const winston = require("winston");

const logger = winston.createLogger({
  level: "info",
  defaultMeta: { service: "vk-backend" },
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      level: "info",
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({
      filename: "backend/logs/error.log",
      level: "error"
    }),
    new winston.transports.File({
      filename: "backend/logs/combined.log",
      level: "info",
      maxsize: 5242880,
      maxFiles: 5
    })
  ]
});

module.exports = logger;