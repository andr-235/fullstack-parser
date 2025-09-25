const multer = require('multer');
const path = require('path');
const logger = require('../utils/logger.js');

// Настройка multer для загрузки файлов
const storage = multer.memoryStorage();

// Фильтр для проверки типа файла
const fileFilter = (req, file, cb) => {
  if (file.mimetype === 'text/plain' || path.extname(file.originalname).toLowerCase() === '.txt') {
    cb(null, true);
  } else {
    cb(new Error('Only .txt files are allowed'), false);
  }
};

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    files: 1 // Только один файл
  }
});

// Middleware для обработки ошибок multer
const handleUploadError = (error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        error: 'INVALID_FILE',
        message: 'File size too large',
        details: {
          allowedTypes: ['.txt']
        }
      });
    }
    if (error.code === 'LIMIT_FILE_COUNT') {
      return res.status(400).json({
        success: false,
        error: 'INVALID_FILE',
        message: 'Only one file allowed',
        details: {
          maxFiles: 1,
          allowedTypes: ['.txt']
        }
      });
    }
  }
  
  if (error.message === 'Only .txt files are allowed') {
      return res.status(400).json({
        success: false,
        error: 'INVALID_FILE',
        message: 'File must be .txt format',
        details: {
          allowedTypes: ['.txt']
        }
      });
  }
  
  logger.error('Upload error', { error: error.message });
  next(error);
};

module.exports = {
  upload: upload.single('file'),
  handleUploadError
};
