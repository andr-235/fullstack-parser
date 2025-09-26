import request from 'supertest';
import fs from 'fs';
import path from 'path';
import app from '../../server';

describe('Groups API Integration Tests', () => {
  const testFilePath = path.join(__dirname, '../../test-groups.txt');
  
  beforeAll(() => {
    // Создаем тестовый файл
    const testContent = `# Тестовый файл групп VK
-123456789  # Валидная группа
-987654321  # Валидная группа
group_name_1  # Группа только с именем
-222222222  # Валидная группа
invalid_id  # Невалидный ID
-333333333  # Валидная группа
group_name_2  # Еще одна группа с именем`;
    
    fs.writeFileSync(testFilePath, testContent);
  });
  
  afterAll(() => {
    // Удаляем тестовый файл
    if (fs.existsSync(testFilePath)) {
      fs.unlinkSync(testFilePath);
    }
  });
  
  jest.mock('../../src/repositories/groupsRepo.js', () => ({
    createGroups: jest.fn().mockResolvedValue(5),
    groupExists: jest.fn().mockResolvedValue(false),
    getGroups: jest.fn().mockResolvedValue({ groups: [], total: 0 }),
    deleteGroup: jest.fn().mockResolvedValue(true),
    deleteGroups: jest.fn().mockResolvedValue(1),
    getGroupsStats: jest.fn().mockResolvedValue({ total: 0, valid: 0, invalid: 0, duplicate: 0 })
  }));

  const groupsRepo = require('../../src/repositories/groupsRepo.js');

  describe('POST /api/groups/upload', () => {
    it('should upload groups file successfully with query encoding', async () => {
      const response = await request(app)
        .post('/api/groups/upload')
        .attach('file', testFilePath)
        .query({ encoding: 'utf-8' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('taskId');
      expect(response.body.data).toHaveProperty('totalGroups');
      expect(response.body.data.totalGroups).toBeGreaterThan(0);
      expect(groupsRepo.createGroups).toHaveBeenCalled();
    });
    
    it('should reject non-txt files', async () => {
      const response = await request(app)
        .post('/api/groups/upload')
        .attach('file', Buffer.from('test content'), 'test.js')
        .query({ encoding: 'utf-8' });
      
      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('INVALID_FILE');
    });
    
    it('should reject requests without file', async () => {
      const response = await request(app)
        .post('/api/groups/upload')
        .query({ encoding: 'utf-8' });
      
      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('NO_FILE');
    });
  });
  
  describe('GET /api/groups/upload/:taskId/status', () => {
    let taskId;
    
    beforeAll(async () => {
      // Создаем задачу загрузки
      const response = await request(app)
        .post('/api/groups/upload')
        .attach('file', testFilePath);
      
      taskId = response.body.data.taskId;
    });
    
    it('should return upload status', async () => {
      const response = await request(app)
        .get(`/api/groups/upload/${taskId}/status`);
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('status');
      expect(response.body.data).toHaveProperty('progress');
    });
    
    it('should return 404 for non-existent task', async () => {
      const response = await request(app)
        .get('/api/groups/upload/non-existent-task/status');
      
      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
    });
  });
  
  describe('GET /api/groups', () => {
    let taskId;
    
    beforeAll(async () => {
      // Создаем задачу загрузки
      const response = await request(app)
        .post('/api/groups/upload')
        .attach('file', testFilePath);
      
      taskId = response.body.data.taskId;
    });
    
    it('should return groups list', async () => {
      const response = await request(app)
        .get(`/api/groups?taskId=${taskId}&limit=10&offset=0`);
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('groups');
      expect(response.body).toHaveProperty('total');
      expect(response.body).toHaveProperty('pagination');
    });
    
    it('should require taskId parameter', async () => {
      const response = await request(app)
        .get('/api/groups');
      
      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('MISSING_TASK_ID');
    });
  });
  
  describe('GET /api/groups/:taskId/stats', () => {
    let taskId;
    
    beforeAll(async () => {
      // Создаем задачу загрузки
      const response = await request(app)
        .post('/api/groups/upload')
        .attach('file', testFilePath);
      
      taskId = response.body.data.taskId;
    });
    
    it('should return groups statistics', async () => {
      const response = await request(app)
        .get(`/api/groups/${taskId}/stats`);
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('total');
      expect(response.body).toHaveProperty('valid');
      expect(response.body).toHaveProperty('invalid');
      expect(response.body).toHaveProperty('duplicate');
    });
  });
});
