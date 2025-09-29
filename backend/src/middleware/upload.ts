import multer, { MulterError } from 'multer';
import path from 'path';
import { Request, Response, NextFunction } from 'express';
import { StatusCodes } from 'http-status-codes';
import logger from '@/utils/logger';

// === КОНФИГУРАЦИЯ ЧЕРЕЗ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ===

const MAX_FILE_SIZE = parseInt(process.env.MAX_FILE_SIZE || '10485760'); // 10MB по умолчанию
const MAX_FILE_COUNT = parseInt(process.env.MAX_FILE_COUNT || '1');
const ALLOWED_MIME_TYPES = process.env.ALLOWED_MIME_TYPES?.split(',') || ['text/plain'];
const ALLOWED_EXTENSIONS = process.env.ALLOWED_EXTENSIONS?.split(',') || ['.txt'];

// === НАСТРОЙКА MULTER ===

// Настройка multer для загрузки файлов в память
const storage = multer.memoryStorage();

// Улучшенный фильтр для проверки типа файла
const fileFilter = (req: Request, file: Express.Multer.File, cb: multer.FileFilterCallback): void => {
  const fileExtension = path.extname(file.originalname).toLowerCase();
  const isValidMimeType = ALLOWED_MIME_TYPES.includes(file.mimetype);
  const isValidExtension = ALLOWED_EXTENSIONS.includes(fileExtension);

  if (isValidMimeType && isValidExtension) {
    cb(null, true);
  } else {
    const allowedTypes = ALLOWED_EXTENSIONS.join(', ');
    cb(new Error(`Only ${allowedTypes} files are allowed`));
  }
};

const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: MAX_FILE_SIZE,
    files: MAX_FILE_COUNT
  }
});

// === ОБРАБОТКА ОШИБОК ===

/**
 * Middleware для обработки ошибок multer с использованием http-status-codes
 */
const handleUploadError = (error: Error, req: Request, res: Response, next: NextFunction): void => {
  if (error instanceof MulterError) {
    const maxSizeMB = Math.round(MAX_FILE_SIZE / 1024 / 1024);

    switch (error.code) {
      case 'LIMIT_FILE_SIZE':
        res.error(`File size too large (max ${maxSizeMB}MB)`, StatusCodes.BAD_REQUEST);
        return;

      case 'LIMIT_FILE_COUNT':
        res.error(`Too many files (max ${MAX_FILE_COUNT} file${MAX_FILE_COUNT > 1 ? 's' : ''})`, StatusCodes.BAD_REQUEST);
        return;

      case 'LIMIT_UNEXPECTED_FILE':
        res.error('Unexpected field name for file upload', StatusCodes.BAD_REQUEST);
        return;

      case 'LIMIT_PART_COUNT':
        res.error('Too many form fields', StatusCodes.BAD_REQUEST);
        return;

      case 'LIMIT_FIELD_KEY':
        res.error('Field name too long', StatusCodes.BAD_REQUEST);
        return;

      case 'LIMIT_FIELD_VALUE':
        res.error('Field value too long', StatusCodes.BAD_REQUEST);
        return;

      default:
        res.error(error.message || 'File upload error', StatusCodes.BAD_REQUEST);
        return;
    }
  }

  // Обработка ошибок фильтра файлов
  if (error.message.includes('files are allowed')) {
    res.error(`Invalid file type. ${error.message}`, StatusCodes.BAD_REQUEST);
    return;
  }

  logger.error('Upload error', {
    error: error.message,
    stack: error.stack,
    requestId: req.requestId
  });
  next(error);
};

// === ВАЛИДАЦИЯ ===

/**
 * Улучшенная валидация загруженного файла
 */
const validateUploadedFile = (req: Request, res: Response, next: NextFunction): void => {
  if (!req.file) {
    res.error('No file uploaded', StatusCodes.BAD_REQUEST);
    return;
  }

  if (!req.file.buffer || req.file.buffer.length === 0) {
    res.error('Uploaded file is empty', StatusCodes.BAD_REQUEST);
    return;
  }

  // Проверяем размер файла (дополнительная проверка)
  if (req.file.size > MAX_FILE_SIZE) {
    const maxSizeMB = Math.round(MAX_FILE_SIZE / 1024 / 1024);
    res.error(`File size exceeds maximum allowed size of ${maxSizeMB}MB`, StatusCodes.BAD_REQUEST);
    return;
  }

  // Дополнительная проверка содержимого файла на валидность UTF-8
  try {
    const content = req.file.buffer.toString('utf-8');
    if (content.length === 0) {
      res.error('File content is empty', StatusCodes.BAD_REQUEST);
      return;
    }

    // Проверяем на подозрительное содержимое (опционально)
    if (process.env.FILE_CONTENT_VALIDATION === 'strict') {
      // Базовая проверка на потенциально опасное содержимое
      if (content.includes('<script>') || content.includes('javascript:')) {
        res.error('File contains potentially dangerous content', StatusCodes.BAD_REQUEST);
        return;
      }
    }
  } catch {
    res.error('File must be valid UTF-8 text', StatusCodes.BAD_REQUEST);
    return;
  }

  logger.info('File upload validated', {
    filename: req.file.originalname,
    size: req.file.size,
    mimetype: req.file.mimetype,
    requestId: req.requestId
  });

  next();
};

/**
 * Улучшенное middleware для логирования загрузок
 */
const logFileUpload = (req: Request, res: Response, next: NextFunction): void => {
  if (req.file) {
    logger.info('File upload started', {
      filename: req.file.originalname,
      size: req.file.size,
      mimetype: req.file.mimetype,
      sizeFormatted: `${Math.round(req.file.size / 1024)}KB`,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      requestId: req.requestId
    });
  }
  next();
};

// === ЭКСПОРТ ===

export const uploadSingle = upload.single('file');
export { handleUploadError, validateUploadedFile, logFileUpload };

/**
 * Получение текущей конфигурации upload middleware
 */
export const getUploadConfig = () => ({
  maxFileSize: MAX_FILE_SIZE,
  maxFileSizeMB: Math.round(MAX_FILE_SIZE / 1024 / 1024),
  maxFileCount: MAX_FILE_COUNT,
  allowedMimeTypes: ALLOWED_MIME_TYPES,
  allowedExtensions: ALLOWED_EXTENSIONS
});

export default {
  upload: upload.single('file'),
  handleUploadError,
  validateUploadedFile,
  logFileUpload,
  getUploadConfig
};