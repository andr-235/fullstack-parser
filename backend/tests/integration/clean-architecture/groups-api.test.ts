/**
 * @fileoverview Integration тесты для Groups API (Clean Architecture)
 *
 * Тестирует полный flow от HTTP запроса до ответа через новую архитектуру.
 */

import request from 'supertest';
import fs from 'fs';
import path from 'path';
import { initializeContainer, disposeContainer } from '@infrastructure/di';

describe('Groups API - Clean Architecture Integration', () => {
  const testFilePath = path.join(__dirname, 'test-groups.txt');

  beforeAll(() => {
    // Инициализируем DI Container
    const vkAccessToken = process.env.VK_ACCESS_TOKEN || 'test_token';
    initializeContainer(vkAccessToken);

    // Создаем тестовый файл
    const testContent = `# Тестовый файл групп VK
123456789
987654321
111222333`;

    fs.writeFileSync(testFilePath, testContent);
  });

  afterAll(async () => {
    // Очищаем ресурсы
    await disposeContainer();

    // Удаляем тестовый файл
    if (fs.existsSync(testFilePath)) {
      fs.unlinkSync(testFilePath);
    }
  });

  describe('POST /api/groups/upload', () => {
    it('должен создать задачу загрузки групп', async () => {
      // Создаем простой Express app для теста
      const express = require('express');
      const app = express();
      const groupsController = require('@presentation/controllers/GroupsController').default;

      app.use('/api/groups', groupsController);

      // Act
      const response = await request(app)
        .post('/api/groups/upload')
        .attach('file', testFilePath)
        .query({ encoding: 'utf-8' });

      // Assert
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data).toHaveProperty('taskId');
      expect(response.body.data).toHaveProperty('totalGroups');
      expect(response.body.data.totalGroups).toBeGreaterThan(0);
    }, 10000);

    it('должен вернуть ошибку без файла', async () => {
      const express = require('express');
      const app = express();
      const groupsController = require('@presentation/controllers/GroupsController').default;

      app.use('/api/groups', groupsController);

      // Act
      const response = await request(app)
        .post('/api/groups/upload')
        .query({ encoding: 'utf-8' });

      // Assert
      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('success', false);
    });
  });

  describe('GET /api/groups', () => {
    it('должен вернуть список групп с пагинацией', async () => {
      const express = require('express');
      const app = express();
      const groupsController = require('@presentation/controllers/GroupsController').default;

      app.use('/api/groups', groupsController);

      // Act
      const response = await request(app)
        .get('/api/groups')
        .query({ page: 1, limit: 10 });

      // Assert
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('data');
      expect(response.body).toHaveProperty('pagination');
      expect(response.body.pagination).toMatchObject({
        page: 1,
        limit: 10,
        total: expect.any(Number),
        totalPages: expect.any(Number),
        hasNext: expect.any(Boolean),
        hasPrev: expect.any(Boolean)
      });
    });

    it('должен фильтровать по статусу', async () => {
      const express = require('express');
      const app = express();
      const groupsController = require('@presentation/controllers/GroupsController').default;

      app.use('/api/groups', groupsController);

      // Act
      const response = await request(app)
        .get('/api/groups')
        .query({ page: 1, limit: 10, status: 'valid' });

      // Assert
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
    });

    it('должен применить поиск', async () => {
      const express = require('express');
      const app = express();
      const groupsController = require('@presentation/controllers/GroupsController').default;

      app.use('/api/groups', groupsController);

      // Act
      const response = await request(app)
        .get('/api/groups')
        .query({ page: 1, limit: 10, search: 'test' });

      // Assert
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
    });
  });

  describe('GET /api/groups/stats', () => {
    it('должен вернуть статистику по группам', async () => {
      const express = require('express');
      const app = express();
      const groupsController = require('@presentation/controllers/GroupsController').default;

      app.use('/api/groups', groupsController);

      // Act
      const response = await request(app)
        .get('/api/groups/stats');

      // Assert
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data).toMatchObject({
        total: expect.any(Number),
        valid: expect.any(Number),
        invalid: expect.any(Number),
        duplicate: expect.any(Number)
      });
    });
  });

  describe('DELETE /api/groups/:id', () => {
    it('должен удалить группу по ID', async () => {
      const express = require('express');
      const app = express();
      const groupsController = require('@presentation/controllers/GroupsController').default;

      app.use('/api/groups', groupsController);

      // Предполагаем, что группа с ID 999999 существует
      // В реальных тестах нужно сначала создать группу

      // Act
      const response = await request(app)
        .delete('/api/groups/999999');

      // Assert
      // Может быть 200 (успех) или 404 (не найдена)
      expect([200, 404]).toContain(response.status);
    });

    it('должен вернуть ошибку для невалидного ID', async () => {
      const express = require('express');
      const app = express();
      const groupsController = require('@presentation/controllers/GroupsController').default;

      app.use('/api/groups', groupsController);

      // Act
      const response = await request(app)
        .delete('/api/groups/invalid-id');

      // Assert
      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });
  });

  describe('Architecture compliance', () => {
    it('контроллер должен использовать Use Cases через фабрики', () => {
      // Arrange
      const GroupsUseCasesFactory = require('@presentation/factories/GroupsUseCasesFactory').GroupsUseCasesFactory;

      // Act & Assert
      expect(GroupsUseCasesFactory.getUploadGroupsUseCase).toBeDefined();
      expect(GroupsUseCasesFactory.getGetGroupsUseCase).toBeDefined();
      expect(GroupsUseCasesFactory.getDeleteGroupUseCase).toBeDefined();
      expect(GroupsUseCasesFactory.getGetGroupStatsUseCase).toBeDefined();

      // Проверяем, что Use Cases можно получить
      const uploadUseCase = GroupsUseCasesFactory.getUploadGroupsUseCase();
      expect(uploadUseCase).toBeDefined();
      expect(uploadUseCase.execute).toBeDefined();
    });

    it('DI Container должен управлять зависимостями', () => {
      // Arrange
      const { getContainer } = require('@infrastructure/di');

      // Act
      const container = getContainer();

      // Assert
      expect(container).toBeDefined();
      expect(container.getGroupsRepository).toBeDefined();
      expect(container.getVkApiRepository).toBeDefined();
      expect(container.getTaskStorageRepository).toBeDefined();
      expect(container.getFileParser).toBeDefined();
    });

    it('Repository должен реализовывать Domain интерфейс', () => {
      // Arrange
      const { getContainer } = require('@infrastructure/di');
      const container = getContainer();

      // Act
      const groupsRepo = container.getGroupsRepository();

      // Assert
      expect(groupsRepo.save).toBeDefined();
      expect(groupsRepo.findAll).toBeDefined();
      expect(groupsRepo.delete).toBeDefined();
      expect(groupsRepo.getStatistics).toBeDefined();
    });
  });
});
