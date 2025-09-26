const FileParser = require('../../src/utils/fileParser.js');
const fs = require('fs').promises;
const path = require('path');

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
    it('should parse groups file correctly', async () => {
      const result = await FileParser.parseGroupsFile(testFilePath, 'utf-8');
      
      expect(result).toHaveProperty('groups');
      expect(result).toHaveProperty('errors');
      expect(result).toHaveProperty('totalLines');
      
      expect(result.totalLines).toBe(11); // Количество строк в файле
      expect(result.groups.length).toBeGreaterThan(0);
      expect(result.errors.length).toBeGreaterThan(0);
    });
    
    it('should handle UTF-8 encoding with mock fs', async () => {
      const mockFs = require('fs').promises;
      const mockReadFile = jest.spyOn(mockFs, 'readFile').mockResolvedValue(Buffer.from('-123456\n-789012\ninvalid\n', 'utf-8'));
      
      const result = await FileParser.parseGroupsFile('mock/path.txt', 'utf-8');
      
      expect(mockReadFile).toHaveBeenCalledWith('mock/path.txt', 'utf-8');
      expect(result.groups).toHaveLength(2);
      expect(result.groups[0].id).toBe(-123456);
      expect(result.groups[1].id).toBe(-789012);
      expect(result.errors).toHaveLength(1);
      
      mockReadFile.mockRestore();
    });
    
    it('should throw error for non-existent file', async () => {
      await expect(
        FileParser.parseGroupsFile('/non/existent/file.txt')
      ).rejects.toThrow('Failed to parse file');
    });
  });
  
  describe('parseGroupLine', () => {
    it('should parse valid group ID', () => {
      const result = FileParser.parseGroupLine('-123456789', 1);
      expect(result).toEqual({
        id: -123456789,
        name: null,
        lineNumber: 1
      });
    });
    
    it('should parse valid group name', () => {
      const result = FileParser.parseGroupLine('group_name', 1);
      expect(result).toEqual({
        id: null,
        name: 'group_name',
        lineNumber: 1
      });
    });
    
    it('should throw error for invalid group ID (positive)', () => {
      expect(() => {
        FileParser.parseGroupLine('123456789', 1);
      }).toThrow('Group ID must be negative');
    });
    
    it('should throw error for invalid format', () => {
      expect(() => {
        FileParser.parseGroupLine('-invalid-format', 1);
      }).toThrow('Invalid group format');
    });
  });
  
  describe('validateFile', () => {
    it('should validate correct file', async () => {
      const result = await FileParser.validateFile(testFilePath);
      expect(result).toBe(true);
    });
    
    it('should throw error for non-existent file', async () => {
      await expect(
        FileParser.validateFile('/non/existent/file.txt')
      ).rejects.toThrow('ENOENT');
    });
    
    it('should throw error for non-txt file', async () => {
      const nonTxtFile = path.join(testDir, 'test.txt');
      await fs.writeFile(nonTxtFile, 'test', 'utf-8');
      
      // Переименовываем в .js
      const jsFile = path.join(testDir, 'test.js');
      await fs.rename(nonTxtFile, jsFile);
      
      await expect(
        FileParser.validateFile(jsFile)
      ).rejects.toThrow('File must have .txt extension');
      
      // Очищаем
      await fs.unlink(jsFile);
    });
  });
});
