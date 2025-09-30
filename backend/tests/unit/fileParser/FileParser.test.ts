import fs from 'fs';
import path from 'path';
import { FileParser } from '@/utils/fileParser/FileParser';
import { FileParserFactory } from '@/utils/fileParser/FileParserFactory';
import { ValidationError } from '@/utils/errors';

describe('FileParser', () => {
  const testFilesDir = path.join(__dirname, 'test-files');
  let parser: FileParser;

  beforeAll(async () => {
    // Создаем директорию для тестовых файлов
    if (!fs.existsSync(testFilesDir)) {
      fs.mkdirSync(testFilesDir, { recursive: true });
    }
  });

  beforeEach(() => {
    parser = FileParserFactory.create();
  });

  afterAll(async () => {
    // Очищаем тестовые файлы
    if (fs.existsSync(testFilesDir)) {
      const files = fs.readdirSync(testFilesDir);
      files.forEach(file => {
        fs.unlinkSync(path.join(testFilesDir, file));
      });
      fs.rmdirSync(testFilesDir);
    }
  });

  describe('parseGroupsFile()', () => {
    it('should parse file with various formats', async () => {
      const testFile = path.join(testFilesDir, 'mixed-formats.txt');
      const content = [
        'https://vk.com/club123',
        'https://vk.com/durov',
        '-456',
        '789',
        'testgroup',
        'club999'
      ].join('\n');
      fs.writeFileSync(testFile, content, 'utf-8');

      const result = await parser.parseGroupsFile(testFile);

      expect(result.groups).toHaveLength(6);
      expect(result.errors).toHaveLength(0);
      expect(result.totalProcessed).toBe(6);

      expect(result.groups[0]).toMatchObject({ id: 123, name: '', url: 'https://vk.com/club123' });
      expect(result.groups[1]).toMatchObject({ id: 0, name: 'durov', url: 'https://vk.com/durov' });
      expect(result.groups[2]).toMatchObject({ id: 456, name: '', url: 'https://vk.com/club456' });
      expect(result.groups[3]).toMatchObject({ id: 789, name: '', url: 'https://vk.com/club789' });
      expect(result.groups[4]).toMatchObject({ id: 0, name: 'testgroup', url: 'https://vk.com/testgroup' });
      expect(result.groups[5]).toMatchObject({ id: 999, name: 'club999', url: 'https://vk.com/club999' });
    });

    it('should parse screen_names with dots', async () => {
      const testFile = path.join(testFilesDir, 'with-dots.txt');
      const content = [
        'https://vk.com/baraholka777.birobidzhan',
        'https://vk.com/valera.naito',
        'q.online',
        'test.group.name',
        'my_group.test'
      ].join('\n');
      fs.writeFileSync(testFile, content, 'utf-8');

      const result = await parser.parseGroupsFile(testFile);

      expect(result.groups).toHaveLength(5);
      expect(result.errors).toHaveLength(0);
      expect(result.groups[0]).toMatchObject({ id: 0, name: 'baraholka777.birobidzhan', url: 'https://vk.com/baraholka777.birobidzhan' });
      expect(result.groups[1]).toMatchObject({ id: 0, name: 'valera.naito', url: 'https://vk.com/valera.naito' });
      expect(result.groups[2]).toMatchObject({ id: 0, name: 'q.online', url: 'https://vk.com/q.online' });
      expect(result.groups[3]).toMatchObject({ id: 0, name: 'test.group.name', url: 'https://vk.com/test.group.name' });
      expect(result.groups[4]).toMatchObject({ id: 0, name: 'my_group.test', url: 'https://vk.com/my_group.test' });
    });

    it('should handle comments and empty lines', async () => {
      const testFile = path.join(testFilesDir, 'with-comments.txt');
      const content = [
        '# This is a comment',
        'https://vk.com/club123',
        '',
        '  ',
        '456 # inline comment',
        ''
      ].join('\n');
      fs.writeFileSync(testFile, content, 'utf-8');

      const result = await parser.parseGroupsFile(testFile);

      expect(result.groups).toHaveLength(2);
      expect(result.errors).toHaveLength(0);
      expect(result.groups[0].id).toBe(123);
      expect(result.groups[1].id).toBe(456);
    });

    it('should detect duplicates', async () => {
      const testFile = path.join(testFilesDir, 'duplicates.txt');
      const content = [
        'https://vk.com/club123',
        '-123',
        '456',
        '456'
      ].join('\n');
      fs.writeFileSync(testFile, content, 'utf-8');

      const result = await parser.parseGroupsFile(testFile);

      expect(result.groups).toHaveLength(2);
      expect(result.errors).toHaveLength(2);
      expect(result.errors[0]).toContain('Duplicate group ID 123');
      expect(result.errors[1]).toContain('Duplicate group ID 456');
    });

    it('should handle invalid formats', async () => {
      const testFile = path.join(testFilesDir, 'invalid.txt');
      const content = [
        'invalid@#$%',
        'https://invalid.com/test',
        '123',
        'test-group'
      ].join('\n');
      fs.writeFileSync(testFile, content, 'utf-8');

      const result = await parser.parseGroupsFile(testFile);

      expect(result.groups).toHaveLength(1); // Только 123 валидный
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should include metadata in result', async () => {
      const testFile = path.join(testFilesDir, 'metadata-test.txt');
      const content = ['123', '456', '789'].join('\n');
      fs.writeFileSync(testFile, content, 'utf-8');

      const result = await parser.parseGroupsFile(testFile);

      expect(result.metadata).toBeDefined();
      expect(result.metadata?.parseTimeMs).toBeGreaterThanOrEqual(0);
      expect(result.metadata?.successRate).toBeGreaterThan(0);
      expect(result.metadata?.duplicatesFound).toBe(0);
      expect(result.metadata?.strategiesUsed).toBeDefined();
    });

    it('should handle different encodings', async () => {
      const testFile = path.join(testFilesDir, 'utf8-test.txt');
      const content = 'https://vk.com/club123\n456';
      fs.writeFileSync(testFile, content, 'utf-8');

      const result = await parser.parseGroupsFile(testFile, 'utf-8');

      expect(result.groups).toHaveLength(2);
    });

    it('should throw error for non-existent file', async () => {
      const nonExistentFile = path.join(testFilesDir, 'non-existent.txt');

      await expect(parser.parseGroupsFile(nonExistentFile)).rejects.toThrow();
    });
  });

  describe('validateFile()', () => {
    it('should validate correct file', async () => {
      const testFile = path.join(testFilesDir, 'valid.txt');
      fs.writeFileSync(testFile, 'test content', 'utf-8');

      const result = await parser.validateFile(testFile);

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.data).toBeDefined();
      expect(result.data?.extension).toBe('txt');
    });

    it('should reject file with wrong extension', async () => {
      const testFile = path.join(testFilesDir, 'wrong.csv');
      fs.writeFileSync(testFile, 'test content', 'utf-8');

      const result = await parser.validateFile(testFile);

      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain('extension');
    });

    it('should reject file exceeding size limit', async () => {
      const testFile = path.join(testFilesDir, 'large.txt');
      // Создаем файл размером больше 10MB
      const largeContent = 'x'.repeat(11 * 1024 * 1024);
      fs.writeFileSync(testFile, largeContent, 'utf-8');

      const result = await parser.validateFile(testFile);

      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain('size');

      // Удаляем большой файл
      fs.unlinkSync(testFile);
    });

    it('should handle non-existent file', async () => {
      const nonExistentFile = path.join(testFilesDir, 'non-existent.txt');

      const result = await parser.validateFile(nonExistentFile);

      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe('isFileAccessible()', () => {
    it('should return true for accessible file', async () => {
      const testFile = path.join(testFilesDir, 'accessible.txt');
      fs.writeFileSync(testFile, 'test', 'utf-8');

      const result = await parser.isFileAccessible(testFile);

      expect(result).toBe(true);
    });

    it('should return false for non-existent file', async () => {
      const nonExistentFile = path.join(testFilesDir, 'non-existent.txt');

      const result = await parser.isFileAccessible(nonExistentFile);

      expect(result).toBe(false);
    });
  });

  describe('getFileStats()', () => {
    it('should return stats for existing file', async () => {
      const testFile = path.join(testFilesDir, 'stats-test.txt');
      fs.writeFileSync(testFile, 'test content', 'utf-8');

      const stats = await parser.getFileStats(testFile);

      expect(stats).not.toBeNull();
      expect(stats?.size).toBeGreaterThan(0);
    });

    it('should return null for non-existent file', async () => {
      const nonExistentFile = path.join(testFilesDir, 'non-existent.txt');

      const stats = await parser.getFileStats(nonExistentFile);

      expect(stats).toBeNull();
    });
  });

  describe('getLineParser()', () => {
    it('should return GroupLineParser instance', () => {
      const lineParser = parser.getLineParser();

      expect(lineParser).toBeDefined();
      expect(lineParser.getStrategies().length).toBeGreaterThan(0);
    });

    it('should allow adding custom strategies', () => {
      const lineParser = parser.getLineParser();
      const initialCount = lineParser.getStrategies().length;

      lineParser.addStrategy({
        name: 'custom',
        priority: 10,
        description: 'Custom',
        canParse: () => false,
        parse: () => null
      });

      expect(lineParser.getStrategies().length).toBe(initialCount + 1);
    });
  });

  describe('FileParserFactory', () => {
    it('should create parser with default config', () => {
      const parser = FileParserFactory.create();
      expect(parser).toBeInstanceOf(FileParser);
    });

    it('should create parser with custom config', () => {
      const parser = FileParserFactory.create({ maxFileSizeMb: 20 });
      expect(parser).toBeInstanceOf(FileParser);
    });

    it('should create parser with large file support', () => {
      const parser = FileParserFactory.createWithLargeFileSupport(50);
      expect(parser).toBeInstanceOf(FileParser);
    });

    it('should create parser with custom encoding', () => {
      const parser = FileParserFactory.createWithEncoding('utf-8');
      expect(parser).toBeInstanceOf(FileParser);
    });
  });

  describe('Performance and metrics', () => {
    it('should track parsing metrics', async () => {
      const testFile = path.join(testFilesDir, 'metrics.txt');
      const content = [
        'https://vk.com/club123',
        'https://vk.com/durov',
        '-456',
        '789'
      ].join('\n');
      fs.writeFileSync(testFile, content, 'utf-8');

      const result = await parser.parseGroupsFile(testFile);

      expect(result.metadata).toBeDefined();
      expect(result.metadata?.parseTimeMs).toBeGreaterThanOrEqual(0);
      expect(result.metadata?.successRate).toBe(1.0); // 4/4
      expect(result.metadata?.strategiesUsed).toBeDefined();
      expect(Object.keys(result.metadata?.strategiesUsed || {}).length).toBeGreaterThan(0);
    });
  });
});