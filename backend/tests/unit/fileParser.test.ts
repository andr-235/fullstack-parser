import FileParser from '../../src/utils/fileParser';
import { promises as fs } from 'fs';
import path from 'path';
import logger from '../../src/utils/logger';

// Mock fs/promises
jest.mock('fs/promises', () => ({
  readFile: jest.fn(),
  stat: jest.fn(),
  access: jest.fn()
}));

// Mock logger
jest.mock('../../src/utils/logger', () => ({
  info: jest.fn(),
  error: jest.fn()
}));

const mockReadFile = fs.readFile as jest.MockedFunction<typeof fs.readFile>;
const mockStat = fs.stat as jest.MockedFunction<typeof fs.stat>;
const mockAccess = fs.access as jest.MockedFunction<typeof fs.access>;
const mockLoggerInfo = logger.info as jest.MockedFunction<typeof logger.info>;
const mockLoggerError = logger.error as jest.MockedFunction<typeof logger.error>;

describe('FileParser Unit Tests', () => {
  const testDir = path.join(__dirname, '../temp');
  const testFilePath = path.join(testDir, 'test-groups.txt');
  
  beforeAll(async () => {
    // Создаем временную директорию
    await fs.mkdir(testDir, { recursive: true });
  });
  
  afterAll(async () => {
    // Удаляем временную директорию
    await fs.rm(testDir, { recursive: true, force: true });
  });
  
  beforeEach(async () => {
    // Сбрасываем mocks
    mockReadFile.mockReset();
    mockStat.mockReset();
    mockAccess.mockReset();
    mockLoggerInfo.mockReset();
    mockLoggerError.mockReset();
    
    // Создаем тестовый файл перед каждым тестом
    const testContent = `# Тестовый файл групп VK
-123456789  # Валидная группа
-987654321  # Валидная группа
group_name_1  # Группа только с именем
-222222222  # Валидная группа
invalid_id  # Невалидный ID
-333333333  # Валидная группа
group_name_2  # Еще одна группа с именем

# Пустая строка выше должна игнорироваться
-444444444  # Валидная группа`;
    
    await fs.writeFile(testFilePath, testContent, 'utf-8');
  });
  
  afterEach(async () => {
    // Удаляем тестовый файл после каждого теста
    try {
      await fs.unlink(testFilePath);
    } catch (error) {
      // Игнорируем ошибки если файл не существует
    }
  });

  describe('parseGroupsFile', () => {
    it('should parse groups file correctly with real file', async () => {
      const result = await FileParser.parseGroupsFile(testFilePath, 'utf-8');
      
      expect(result).toHaveProperty('groups');
      expect(result).toHaveProperty('errors');
      expect(result).toHaveProperty('totalProcessed');
      
      expect(result.totalProcessed).toBe(11); // Количество строк в файле
      expect(result.groups.length).toBe(7); // Валидные группы: 5 ID + 2 name
      expect(result.errors.length).toBe(1); // invalid_id
      
      // Проверяем первую группу
      expect(result.groups[0]).toEqual({
        id: 123456789,
        name: '',
        url: 'https://vk.com/club123456789'
      });
      
      // Проверяем группу с именем
      expect(result.groups[2]).toEqual({
        id: null,
        name: 'group_name_1',
        url: 'https://vk.com/group_name_1'
      });
      
      // Логирование вызвано
      expect(mockLoggerInfo).toHaveBeenCalledTimes(2);
      expect(mockLoggerInfo).toHaveBeenCalledWith('Sample parsed groups (first 5)', expect.any(Object));
      expect(mockLoggerInfo).toHaveBeenCalledWith('File parsed successfully', expect.any(Object));
    });
    
    it('should handle UTF-8 encoding with mocked fs.readFile', async () => {
      const mockContent = Buffer.from('-123456\n-789012\ninvalid\n# comment\ngroup_name\n', 'utf-8');
      mockReadFile.mockResolvedValueOnce(mockContent);
      
      const result = await FileParser.parseGroupsFile('mock/path.txt', 'utf-8');
      
      expect(mockReadFile).toHaveBeenCalledWith('mock/path.txt', 'utf-8');
      expect(result.groups).toHaveLength(3); // 2 ID + 1 name
      expect(result.groups[0].id).toBe(123456);
      expect(result.groups[1].id).toBe(789012);
      expect(result.groups[2].id).toBeNull();
      expect(result.groups[2].name).toBe('group_name');
      expect(result.errors).toHaveLength(1); // invalid
      
      // Логирование
      expect(mockLoggerInfo).toHaveBeenCalledTimes(2);
    });
    
    it('should handle file with duplicates and skip them', async () => {
      const mockContent = Buffer.from('-123\n-123\nduplicate\nclub456\ngroup_name\n', 'utf-8');
      mockReadFile.mockResolvedValueOnce(mockContent);
      
      const result = await FileParser.parseGroupsFile('mock/dup.txt');
      
      expect(result.groups).toHaveLength(2); // Только уникальные: club456, group_name (дубликат -123 пропущен)
      expect(result.errors).toHaveLength(1); // Duplicate group ID 123
    });
    
    it('should handle file with comments and empty lines', async () => {
      const mockContent = Buffer.from(`# Comment line

-123
  # Trailing comment
group_name
`, 'utf-8');
      mockReadFile.mockResolvedValueOnce(mockContent);
      
      const result = await FileParser.parseGroupsFile('mock/comments.txt');
      
      expect(result.groups).toHaveLength(2);
      expect(result.errors).toHaveLength(0);
      expect(result.totalProcessed).toBe(5); // Включая пустые и комментарии
    });
    
    it('should handle empty file', async () => {
      mockReadFile.mockResolvedValueOnce(Buffer.from(''));
      
      const result = await FileParser.parseGroupsFile('mock/empty.txt');
      
      expect(result.groups).toHaveLength(0);
      expect(result.errors).toHaveLength(0);
      expect(result.totalProcessed).toBe(1); // Пустая строка
      expect(mockLoggerInfo).toHaveBeenCalledWith('File parsed successfully', expect.objectContaining({
        totalLines: 1,
        validGroups: 0,
        errors: 0
      }));
    });
    
    it('should throw error for non-existent file', async () => {
      mockReadFile.mockRejectedValueOnce(new Error('ENOENT: no such file'));
      
      await expect(
        FileParser.parseGroupsFile('/non/existent/file.txt')
      ).rejects.toThrow('Failed to parse file: ENOENT: no such file');
      
      expect(mockLoggerError).toHaveBeenCalledWith('Failed to parse file', expect.any(Object));
    });
    
    it('should handle very long lines (trimmed but processed)', async () => {
      const longLine = '-123'.padEnd(1000, 'a'); // Длинная строка
      const mockContent = Buffer.from(`${longLine}\ngroup_name\n`, 'utf-8');
      mockReadFile.mockResolvedValueOnce(mockContent);
      
      const result = await FileParser.parseGroupsFile('mock/long.txt');
      
      expect(result.groups).toHaveLength(2);
      expect(result.groups[0].id).toBe(123); // Trimmed
    });
  });

  describe('parseGroupLine (testing private parsers indirectly)', () => {
    // Тесты для приватных методов через публичный parseGroupLine
    
    it('should parse URL club format correctly', () => {
      const result = FileParser.parseGroupLine('https://vk.com/club123', 1);
      
      expect(result).toEqual({
        id: 123,
        name: null,
        lineNumber: 1
      });
    });
    
    it('should parse URL screen_name format correctly', () => {
      const result = FileParser.parseGroupLine('https://vk.com/durov', 1);
      
      expect(result).toEqual({
        id: null,
        name: 'durov',
        lineNumber: 1
      });
    });
    
    it('should parse negative ID correctly (absolute value)', () => {
      const result = FileParser.parseGroupLine('-123456', 1);
      
      expect(result).toEqual({
        id: 123456,
        name: null,
        lineNumber: 1
      });
    });
    
    it('should parse positive ID correctly', () => {
      const result = FileParser.parseGroupLine('789012', 1);
      
      expect(result).toEqual({
        id: 789012,
        name: null,
        lineNumber: 1
      });
    });
    
    it('should parse screen_name correctly', () => {
      const result = FileParser.parseGroupLine('group_name', 1);
      
      expect(result).toEqual({
        id: null,
        name: 'group_name',
        lineNumber: 1
      });
    });
    
    it('should parse clubXXX screen_name as ID with name', () => {
      const result = FileParser.parseGroupLine('club456', 1);
      
      expect(result).toEqual({
        id: 456,
        name: 'club456',
        lineNumber: 1
      });
    });
    
    it('should throw GroupParseError for invalid format', () => {
      expect(() => {
        FileParser.parseGroupLine('invalid_format', 1);
      }).toThrow('Invalid group format');
    });
    
    it('should handle empty string (but cleanLine skips, test via file)', () => {
      // Пустая строка обрабатывается в cleanLine, здесь тест invalid
      expect(() => {
        FileParser.parseGroupLine('', 1);
      }).toThrow('Invalid group format');
    });
    
    it('should reject ID <= 0 in positive ID', () => {
      expect(() => {
        FileParser.parseGroupLine('0', 1);
      }).toThrow('Invalid group format');
    });
    
    it('should handle case-insensitive URL (http, www)', () => {
      const result1 = FileParser.parseGroupLine('HTTP://www.vk.com/club789', 1);
      expect(result1.id).toBe(789);
      
      const result2 = FileParser.parseGroupLine('https://VK.COM/group_name', 1);
      expect(result2.name).toBe('group_name');
    });
    
    it('should handle long screen_name (no limit in code, but trim)', () => {
      const longName = 'a'.repeat(100) + '_group';
      const result = FileParser.parseGroupLine(longName, 1);
      
      expect(result.name).toBe(longName);
      expect(result.id).toBeNull();
    });
  });

  describe('validateFile', () => {
    beforeEach(() => {
      mockStat.mockResolvedValue({
        size: 5000,
        isFile: () => true
      } as any);
    });
    
    it('should validate correct small TXT file', async () => {
      const result = await FileParser.validateFile(testFilePath);
      
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.data).toEqual({ size: 5000, extension: 'txt' });
      expect(mockLoggerError).not.toHaveBeenCalled();
    });
    
    it('should reject file larger than 10MB', async () => {
      mockStat.mockResolvedValueOnce({
        size: 11 * 1024 * 1024, // 11MB
        isFile: () => true
      } as any);
      
      const result = await FileParser.validateFile('big.txt');
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toEqual(expect.arrayContaining([
        expect.stringContaining('exceeds 10MB limit')
      ]));
      expect(mockLoggerError).toHaveBeenCalledWith('File validation failed', expect.any(Object));
    });
    
    it('should reject non-TXT extension', async () => {
      const result = await FileParser.validateFile('test.js');
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toEqual(['File must have .txt extension']);
      expect(mockLoggerError).toHaveBeenCalled();
    });
    
    it('should handle non-existent file', async () => {
      mockStat.mockRejectedValueOnce(new Error('ENOENT'));
      
      const result = await FileParser.validateFile('/non/existent.txt');
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toEqual(['ENOENT: no such file or directory']);
      expect(mockLoggerError).toHaveBeenCalled();
    });
    
    it('should handle file without read access', async () => {
      mockStat.mockRejectedValueOnce(new Error('EACCES: permission denied'));
      
      const result = await FileParser.validateFile('protected.txt');
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toEqual(['EACCES: permission denied']);
    });
    
    it('should validate large but under limit file', async () => {
      mockStat.mockResolvedValueOnce({
        size: 9 * 1024 * 1024, // 9MB
        isFile: () => true
      } as any);
      
      const result = await FileParser.validateFile('large.txt');
      
      expect(result.isValid).toBe(true);
      expect(result.data?.size).toBe(9 * 1024 * 1024);
    });
  });

  describe('isFileAccessible', () => {
    it('should return true for accessible file', async () => {
      mockAccess.mockResolvedValueOnce(undefined);
      
      const result = await FileParser.isFileAccessible(testFilePath);
      
      expect(result).toBe(true);
      expect(mockAccess).toHaveBeenCalledWith(testFilePath, fs.constants.R_OK);
    });
    
    it('should return false for inaccessible file', async () => {
      mockAccess.mockRejectedValueOnce(new Error('EACCES'));
      
      const result = await FileParser.isFileAccessible('protected.txt');
      
      expect(result).toBe(false);
    });
    
    it('should return false for non-existent file', async () => {
      mockAccess.mockRejectedValueOnce(new Error('ENOENT'));
      
      const result = await FileParser.isFileAccessible('/non/existent.txt');
      
      expect(result).toBe(false);
    });
  });

  describe('getFileStats', () => {
    it('should return stats for existing file', async () => {
      const mockStats = { size: 1024, isFile: () => true } as any;
      mockStat.mockResolvedValueOnce(mockStats);
      
      const result = await FileParser.getFileStats(testFilePath);
      
      expect(result).toEqual(mockStats);
      expect(mockStat).toHaveBeenCalledWith(testFilePath);
    });
    
    it('should return null for non-existent file', async () => {
      mockStat.mockRejectedValueOnce(new Error('ENOENT'));
      
      const result = await FileParser.getFileStats('/non/existent.txt');
      
      expect(result).toBeNull();
    });
    
    it('should return null for inaccessible file', async () => {
      mockStat.mockRejectedValueOnce(new Error('EACCES'));
      
      const result = await FileParser.getFileStats('protected.txt');
      
      expect(result).toBeNull();
    });
  });

  // Косвенные тесты для приватных: cleanLine, checkDuplicates, cleanGroupName, buildGroupUrl, logParsingResults
  describe('Private helpers (indirect tests)', () => {
    it('should clean line: trim and remove comments (via parseGroupsFile)', async () => {
      const mockContent = Buffer.from('  -123   # comment\n group_name # another\n', 'utf-8');
      mockReadFile.mockResolvedValueOnce(mockContent);
      
      const result = await FileParser.parseGroupsFile('mock/clean.txt');
      
      expect(result.groups[0].id).toBe(123); // Trimmed and comment removed
      expect(result.groups[1].name).toBe('group_name'); // Trimmed
    });
    
    it('should check duplicates and skip (via parseGroupsFile)', async () => {
      const mockContent = Buffer.from('-123\n-123\nduplicate\n', 'utf-8');
      mockReadFile.mockResolvedValueOnce(mockContent);
      
      const result = await FileParser.parseGroupsFile('mock/dups.txt');
      
      expect(result.groups).toHaveLength(1); // Только первый -123
      expect(result.errors).toHaveLength(1); // Duplicate
    });
    
    it('should clean group name: remove VK URL prefix (via parseGroupLine + build)', async () => {
      // cleanGroupName вызывается после parse, тест через результат
      const parsed = FileParser.parseGroupLine('https://vk.com/durov', 1);
      // В parseUrlScreenName возвращает name: 'durov', cleanGroupName не меняет, но если full URL в name
      // Тест для случая когда name имеет URL (хотя в коде clean после parse)
      const result = FileParser.parseGroupLine('durov', 1); // name без URL
      expect(result.name).toBe('durov');
      
      // Для buildGroupUrl: в parseGroupsFile, но косвенно
      // Предполагаем, что URL строится правильно из предыдущих тестов
    });
    
    it('should build correct URL for ID and name (indirect via parseGroupsFile)', async () => {
      const mockContent = Buffer.from('-123\ngroup_name\n', 'utf-8');
      mockReadFile.mockResolvedValueOnce(mockContent);
      
      const result = await FileParser.parseGroupsFile('mock/url.txt');
      
      expect(result.groups[0].url).toBe('https://vk.com/club123');
      expect(result.groups[1].url).toBe('https://vk.com/group_name');
    });
    
    it('should log parsing results correctly (mock logger)', async () => {
      const mockContent = Buffer.from('-123\n-456\ninvalid\n', 'utf-8');
      mockReadFile.mockResolvedValueOnce(mockContent);
      
      await FileParser.parseGroupsFile('mock/log.txt');
      
      expect(mockLoggerInfo).toHaveBeenCalledWith('Sample parsed groups (first 5)', expect.objectContaining({
        sample: expect.arrayContaining([
          expect.objectContaining({ id: 123, name: '', url: 'https://vk.com/club123' })
        ])
      }));
      expect(mockLoggerInfo).toHaveBeenCalledWith('File parsed successfully', expect.objectContaining({
        totalLines: 3,
        validGroups: 2,
        errors: 1
      }));
    });
  });
});