const fs = require('fs').promises;
const logger = require('./logger.js');

class FileParser {
  /**
   * Парсит TXT файл с группами VK
   * @param {string} filePath - Путь к файлу
   * @param {string} encoding - Кодировка файла (по умолчанию utf-8)
   * @returns {Object} Результат парсинга
   */
  static async parseGroupsFile(filePath, encoding = 'utf-8') {
    try {
      const content = await fs.readFile(filePath, encoding);
      const lines = content.split('\n');
      
      const groups = [];
      const errors = [];
      const duplicateIds = new Set();
      
      for (let i = 0; i < lines.length; i++) {
        const lineNumber = i + 1;
        const line = lines[i].trim();
        
        // Пропускаем пустые строки
        if (!line) continue;
        
        // Удаляем комментарии после #
        const cleanLine = line.split('#')[0].trim();
        if (!cleanLine) continue;
        
        try {
          const parsed = this.parseGroupLine(cleanLine, lineNumber);
          if (parsed) {
            // Проверяем на дубликаты только для групп с ID
            if (parsed.id !== null && parsed.id !== undefined) {
              if (duplicateIds.has(parsed.id)) {
                errors.push({
                  line: lineNumber,
                  content: line,
                  error: 'Duplicate group ID',
                  groupId: parsed.id
                });
                continue;
              }
              duplicateIds.add(parsed.id);
            }
            groups.push(parsed);
          }
        } catch (error) {
          errors.push({
            line: lineNumber,
            content: line,
            error: error.message,
            expectedFormat: 'Negative integer or group name'
          });
        }
      }
      
      logger.info('File parsed successfully', {
        totalLines: lines.length,
        validGroups: groups.length,
        errors: errors.length
      });
      
      return {
        groups,
        errors,
        totalLines: lines.length
      };
    } catch (error) {
      logger.error('Failed to parse file', { filePath, error: error.message });
      throw new Error(`Failed to parse file: ${error.message}`);
    }
  }
  
  /**
   * Парсит одну строку с группой
   * @param {string} line - Строка для парсинга
   * @param {number} lineNumber - Номер строки
   * @returns {Object|null} Объект группы или null
   */
  static parseGroupLine(line, lineNumber) {
    // Проверяем, является ли строка ID группы (отрицательное число)
    if (line.startsWith('-') && /^-\d+$/.test(line)) {
      const groupId = parseInt(line, 10);
      if (groupId >= 0) {
        throw new Error('Group ID must be negative');
      }
      return {
        id: groupId,
        name: null,
        lineNumber
      };
    }
    
    // Если строка является положительным числом
    if (/^\d+$/.test(line)) {
      throw new Error('Group ID must be negative');
    }
    
    // Если строка начинается с - но не является отрицательным числом
    if (line.startsWith('-') && !/^-\d+$/.test(line)) {
      throw new Error('Invalid group format');
    }
    
    // Проверяем, является ли строка именем группы (не начинается с -)
    if (!line.startsWith('-')) {
      // Если это не число, считаем именем группы
      if (!/^\d+$/.test(line)) {
        return {
          id: null,
          name: line,
          lineNumber
        };
      }
    }
    
    // Если мы дошли сюда, значит строка не подходит ни под один формат
    throw new Error('Invalid group format');
  }
  
  /**
   * Валидирует формат файла
   * @param {string} filePath - Путь к файлу
   * @returns {boolean} Валидность файла
   */
  static async validateFile(filePath) {
    try {
      const stats = await fs.stat(filePath);
      
      // Проверяем размер файла (10MB)
      if (stats.size > 10 * 1024 * 1024) {
        throw new Error('File size exceeds 10MB limit');
      }
      
      // Проверяем расширение
      const ext = filePath.toLowerCase().split('.').pop();
      if (ext !== 'txt') {
        throw new Error('File must have .txt extension');
      }
      
      return true;
    } catch (error) {
      logger.error('File validation failed', { filePath, error: error.message });
      throw error;
    }
  }
}

module.exports = FileParser;
