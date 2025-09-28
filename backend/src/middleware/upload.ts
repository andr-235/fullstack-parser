import multer, { MulterError } from 'multer';
import path from 'path';
import { Request, Response, NextFunction } from 'express';
import logger from '@/utils/logger';
import { ApiResponse } from '@/types/express';

// Extend Request type to include file - переопределяем полностью
declare global {
  namespace Express {
    interface Request {
      file?: Express.Multer.File;
    }
  }
}


// Настройка multer для загрузки файлов
const storage = multer.memoryStorage();

// Фильтр для проверки типа файла
const fileFilter = (req: Request, file: Express.Multer.File, cb: multer.FileFilterCallback): void => {
  if (file.mimetype === 'text/plain' || path.extname(file.originalname).toLowerCase() === '.txt') {
    cb(null, true);
  } else {
    cb(new Error('Only .txt files are allowed'));
  }
};

const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB
    files: 1 // Только один файл
  }
});

// Middleware для обработки ошибок multer
const handleUploadError = (error: Error, req: Request, res: Response, next: NextFunction): void => {
  if (error instanceof MulterError) {
    switch (error.code) {
      case 'LIMIT_FILE_SIZE':
        res.error('File size too large (max 10MB)', 400);
        return;

      case 'LIMIT_FILE_COUNT':
        res.error('Only one file allowed', 400);
        return;

      case 'LIMIT_UNEXPECTED_FILE':
        res.error('Unexpected field name for file upload', 400);
        return;

      default:
        res.error(error.message || 'File upload error', 400);
        return;
    }
  }

  if (error.message === 'Only .txt files are allowed') {
    res.error('File must be .txt format', 400);
    return;
  }

  logger.error('Upload error', { error: error.message, stack: error.stack });
  next(error);
};

// Валидация загруженного файла
const validateUploadedFile = (req: Request, res: Response, next: NextFunction): void => {
  if (!req.file) {
    res.error('No file uploaded', 400);
    return;
  }

  if (!req.file.buffer || req.file.buffer.length === 0) {
    res.error('Uploaded file is empty', 400);
    return;
  }

  // Проверяем размер файла
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (req.file.size > maxSize) {
    res.error('File size exceeds maximum allowed size', 400);
    return;
  }

  // Дополнительная проверка содержимого файла
  try {
    const content = req.file.buffer.toString('utf-8');
    if (content.length === 0) {
      res.error('File content is empty', 400);
      return;
    }
  } catch {
    res.error('File must be valid UTF-8 text', 400);
    return;
  }

  logger.info('File upload validated', {
    filename: req.file.originalname,
    size: req.file.size,
    mimetype: req.file.mimetype
  });

  next();
};

// Middleware для логирования загрузок
const logFileUpload = (req: Request, res: Response, next: NextFunction): void => {
  if (req.file) {
    logger.info('File upload started', {
      filename: req.file.originalname,
      size: req.file.size,
      mimetype: req.file.mimetype,
      ip: req.ip,
      userAgent: req.get('User-Agent')
    });
  }
  next();
};

export const uploadSingle = upload.single('file');
export { handleUploadError, validateUploadedFile, logFileUpload };

export default {
  upload: upload.single('file'),
  handleUploadError,
  validateUploadedFile,
  logFileUpload
};