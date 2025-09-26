import multer, { MulterError } from 'multer';
import path from 'path';
import { Request, Response, NextFunction } from 'express';
import logger from '@/utils/logger';
import { FileUpload } from '@/types/common';
import { ApiResponse } from '@/types/express';

// Extend Request type to include file
declare global {
  namespace Express {
    interface Request {
      file?: FileUpload;
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
    let errorResponse: ApiResponse;

    switch (error.code) {
      case 'LIMIT_FILE_SIZE':
        errorResponse = {
          success: false,
          error: 'INVALID_FILE',
          message: 'File size too large (max 10MB)',
          data: {
            allowedTypes: ['.txt'],
            maxSize: '10MB'
          }
        };
        break;

      case 'LIMIT_FILE_COUNT':
        errorResponse = {
          success: false,
          error: 'INVALID_FILE',
          message: 'Only one file allowed',
          data: {
            maxFiles: 1,
            allowedTypes: ['.txt']
          }
        };
        break;

      case 'LIMIT_UNEXPECTED_FILE':
        errorResponse = {
          success: false,
          error: 'INVALID_FILE',
          message: 'Unexpected field name for file upload',
          data: {
            expectedField: 'file',
            allowedTypes: ['.txt']
          }
        };
        break;

      default:
        errorResponse = {
          success: false,
          error: 'UPLOAD_ERROR',
          message: error.message || 'File upload error',
          data: {
            allowedTypes: ['.txt']
          }
        };
    }

    res.status(400).json(errorResponse);
    return;
  }

  if (error.message === 'Only .txt files are allowed') {
    const errorResponse: ApiResponse = {
      success: false,
      error: 'INVALID_FILE',
      message: 'File must be .txt format',
      data: {
        allowedTypes: ['.txt'],
        receivedType: req.file?.mimetype || 'unknown'
      }
    };

    res.status(400).json(errorResponse);
    return;
  }

  logger.error('Upload error', { error: error.message, stack: error.stack });
  next(error);
};

// Валидация загруженного файла
const validateUploadedFile = (req: Request, res: Response, next: NextFunction): void => {
  if (!req.file) {
    const errorResponse: ApiResponse = {
      success: false,
      error: 'NO_FILE',
      message: 'No file uploaded',
      data: {
        requiredField: 'file',
        allowedTypes: ['.txt']
      }
    };

    res.status(400).json(errorResponse);
    return;
  }

  if (!req.file.buffer || req.file.buffer.length === 0) {
    const errorResponse: ApiResponse = {
      success: false,
      error: 'EMPTY_FILE',
      message: 'Uploaded file is empty',
      data: {
        allowedTypes: ['.txt']
      }
    };

    res.status(400).json(errorResponse);
    return;
  }

  // Проверяем размер файла
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (req.file.size > maxSize) {
    const errorResponse: ApiResponse = {
      success: false,
      error: 'FILE_TOO_LARGE',
      message: 'File size exceeds maximum allowed size',
      data: {
        maxSize: '10MB',
        receivedSize: `${Math.round(req.file.size / 1024 / 1024)}MB`,
        allowedTypes: ['.txt']
      }
    };

    res.status(400).json(errorResponse);
    return;
  }

  // Дополнительная проверка содержимого файла
  try {
    const content = req.file.buffer.toString('utf-8');
    if (content.length === 0) {
      const errorResponse: ApiResponse = {
        success: false,
        error: 'EMPTY_FILE',
        message: 'File content is empty',
        data: {
          allowedTypes: ['.txt']
        }
      };

      res.status(400).json(errorResponse);
      return;
    }
  } catch (error) {
    const errorResponse: ApiResponse = {
      success: false,
      error: 'INVALID_ENCODING',
      message: 'File must be valid UTF-8 text',
      data: {
        allowedTypes: ['.txt'],
        requiredEncoding: 'UTF-8'
      }
    };

    res.status(400).json(errorResponse);
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