import request from 'supertest';
import express from 'express';
import { ProgressCalculator } from '@/services/progressCalculator';
import taskController from '@/controllers/taskController';
import { TaskMetrics } from '@/types/task';

// Mock taskService для тестирования без БД
jest.mock('@/services/taskService', () => ({
  default: {
    getTaskStatus: jest.fn()
  }
}));

// Mock logger для тестирования
jest.mock('@/utils/logger', () => ({
  default: {
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    debug: jest.fn()
  }
}));

describe('Progress Calculation Integration', () => {
  let app: express.Application;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    app.use('/api', taskController);

    // Reset mocks
    jest.clearAllMocks();
  });

  describe('ProgressCalculator', () => {
    describe('calculateProgress', () => {
      it('должен корректно рассчитывать прогресс для фазы groups', () => {
        const metrics: TaskMetrics = {
          groupsTotal: 10,
          groupsProcessed: 3,
          postsTotal: 0,
          postsProcessed: 0,
          commentsTotal: 0,
          commentsProcessed: 0,
          estimatedCommentsPerPost: 15
        };

        const result = ProgressCalculator.calculateProgress(metrics);

        expect(result.phase).toBe('groups');
        expect(result.percentage).toBe(18); // 30% групп * 10% + 30% постов * 30% = 3% + 15% = 18%
        expect(result.processed).toBe(18);
        expect(result.total).toBe(100);
        expect(result.phases.groups.progress).toBe(0.3);
        expect(result.phases.groups.completed).toBe(false);
      });

      it('должен переходить в фазу posts после завершения groups', () => {
        const metrics: TaskMetrics = {
          groupsTotal: 5,
          groupsProcessed: 5,
          postsTotal: 100,
          postsProcessed: 40,
          commentsTotal: 1500,
          commentsProcessed: 0,
          estimatedCommentsPerPost: 15
        };

        const result = ProgressCalculator.calculateProgress(metrics);

        expect(result.phase).toBe('posts');
        expect(result.phases.groups.completed).toBe(true);
        expect(result.phases.posts.progress).toBe(0.4); // 40/100
        expect(result.percentage).toBe(22); // 10% + 12% (40% от 30%)
      });

      it('должен переходить в фазу comments после завершения posts', () => {
        const metrics: TaskMetrics = {
          groupsTotal: 5,
          groupsProcessed: 5,
          postsTotal: 100,
          postsProcessed: 100,
          commentsTotal: 1500,
          commentsProcessed: 750,
          estimatedCommentsPerPost: 15
        };

        const result = ProgressCalculator.calculateProgress(metrics);

        expect(result.phase).toBe('comments');
        expect(result.phases.groups.completed).toBe(true);
        expect(result.phases.posts.completed).toBe(true);
        expect(result.phases.comments.progress).toBe(0.5); // 750/1500
        expect(result.percentage).toBe(70); // 10% + 30% + 30% (50% от 60%)
      });

      it('не должен превышать 100% даже при некорректных данных', () => {
        const metrics: TaskMetrics = {
          groupsTotal: 5,
          groupsProcessed: 10, // Больше total
          postsTotal: 100,
          postsProcessed: 200, // Больше total
          commentsTotal: 1500,
          commentsProcessed: 3000, // Больше total
          estimatedCommentsPerPost: 15
        };

        const result = ProgressCalculator.calculateProgress(metrics);

        expect(result.percentage).toBeLessThanOrEqual(100);
        expect(result.processed).toBeLessThanOrEqual(100);
      });

      it('должен использовать оценочный прогресс для комментариев при отсутствии точного total', () => {
        const metrics: TaskMetrics = {
          groupsTotal: 3,
          groupsProcessed: 3,
          postsTotal: 60,
          postsProcessed: 60,
          commentsTotal: 0, // Нет точного значения
          commentsProcessed: 450, // 50% от ожидаемых 900 (60 * 15)
          estimatedCommentsPerPost: 15
        };

        const result = ProgressCalculator.calculateProgress(metrics);

        expect(result.phase).toBe('comments');
        expect(result.phases.comments.progress).toBe(0.5); // 450 / 900
        expect(result.percentage).toBe(70); // 10% + 30% + 30%
      });
    });

    describe('estimateTotal', () => {
      it('должен рассчитывать оценку на основе количества групп', () => {
        const taskData = {
          groups: [
            { id: 1, name: 'Group 1' },
            { id: 2, name: 'Group 2' },
            { id: 3, name: 'Group 3' }
          ]
        };

        const estimate = ProgressCalculator.estimateTotal(taskData);

        // 3 группы * 50 постов * 15 комментариев = 2250
        expect(estimate).toBe(2250);
      });

      it('должен учитывать ограничение maxComments', () => {
        const taskData = {
          groupIds: [1, 2, 3, 4, 5],
          maxComments: 1000
        };

        const estimate = ProgressCalculator.estimateTotal(taskData);

        expect(estimate).toBe(1000); // Ограничено maxComments
      });

      it('должен использовать минимальное значение для пустых данных', () => {
        const taskData = {
          groups: []
        };

        const estimate = ProgressCalculator.estimateTotal(taskData);

        expect(estimate).toBe(100); // Минимальное значение по умолчанию
      });
    });

    describe('validateMetrics', () => {
      it('должен выявлять ошибки когда processed > total', () => {
        const metrics: TaskMetrics = {
          groupsTotal: 5,
          groupsProcessed: 10,
          postsTotal: 100,
          postsProcessed: 150,
          commentsTotal: 1500,
          commentsProcessed: 2000,
          estimatedCommentsPerPost: 15
        };

        const errors = ProgressCalculator.validateMetrics(metrics);

        expect(errors).toHaveLength(3);
        expect(errors).toContain('Groups: processed (10) > total (5)');
        expect(errors).toContain('Posts: processed (150) > total (100)');
        expect(errors).toContain('Comments: processed (2000) > total (1500)');
      });

      it('должен возвращать пустой массив для корректных метрик', () => {
        const metrics: TaskMetrics = {
          groupsTotal: 5,
          groupsProcessed: 3,
          postsTotal: 100,
          postsProcessed: 60,
          commentsTotal: 1500,
          commentsProcessed: 900,
          estimatedCommentsPerPost: 15
        };

        const errors = ProgressCalculator.validateMetrics(metrics);

        expect(errors).toHaveLength(0);
      });
    });

    describe('createMetricsFromTask', () => {
      it('должен создавать метрики из данных задачи', () => {
        const taskStatus = {
          groupIds: [1, 2, 3],
          groupsProcessed: 2,
          metrics: {
            posts: 150,
            comments: 2250
          },
          postsTotal: 150,
          postsProcessed: 100,
          commentsTotal: 2250
        };

        const metrics = ProgressCalculator.createMetricsFromTask(taskStatus);

        expect(metrics.groupsTotal).toBe(3);
        expect(metrics.groupsProcessed).toBe(2);
        expect(metrics.postsTotal).toBe(150);
        expect(metrics.postsProcessed).toBe(100);
        expect(metrics.commentsTotal).toBe(2250);
        expect(metrics.commentsProcessed).toBe(2250);
        expect(metrics.estimatedCommentsPerPost).toBe(15);
      });

      it('должен использовать оценочные значения при отсутствии данных', () => {
        const taskStatus = {
          groupIds: [1, 2],
          metrics: {
            comments: 500
          }
        };

        const metrics = ProgressCalculator.createMetricsFromTask(taskStatus);

        expect(metrics.groupsTotal).toBe(2);
        expect(metrics.commentsProcessed).toBe(500);
        expect(metrics.commentsTotal).toBeGreaterThan(0); // Оценочное значение
      });
    });
  });

  describe('Исправление проблемы processed > total', () => {
    it('старый алгоритм: демонстрация проблемы с произвольным множителем', () => {
      // Эмуляция старого алгоритма
      const posts = 100;
      const comments = 500;
      const oldTotal = Math.max(posts * 10, comments); // Произвольный множитель * 10
      const oldProgress = {
        processed: comments,
        total: oldTotal
      };

      // В этом случае oldTotal = max(1000, 500) = 1000, что корректно
      expect(oldProgress.processed).toBeLessThanOrEqual(oldProgress.total);

      // Но при большем количестве комментариев проблема проявляется:
      const moreComments = 1500;
      const problematicTotal = Math.max(posts * 10, moreComments);
      const problematicProgress = {
        processed: moreComments,
        total: problematicTotal
      };

      // problematicTotal = max(1000, 1500) = 1500
      // И при processed = 1500, total = 1500 - получаем 100%, но это не точно
      expect(problematicProgress.processed).toBe(problematicProgress.total);
    });

    it('новый алгоритм: решение проблемы с весовой системой', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 10,
        groupsProcessed: 10,
        postsTotal: 100,
        postsProcessed: 100,
        commentsTotal: 1500,
        commentsProcessed: 1500,
        estimatedCommentsPerPost: 15
      };

      const result = ProgressCalculator.calculateProgress(metrics);

      // Новый алгоритм всегда использует 100 как total
      expect(result.total).toBe(100);
      expect(result.processed).toBeLessThanOrEqual(result.total);

      // При полном завершении всех фаз получаем точно 100%
      expect(result.percentage).toBe(100);
      expect(result.phases.groups.completed).toBe(true);
      expect(result.phases.posts.completed).toBe(true);
      expect(result.phases.comments.completed).toBe(true);
    });

    it('новый алгоритм: корректная обработка частичного прогресса', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 10,
        groupsProcessed: 5,  // 50% групп
        postsTotal: 100,
        postsProcessed: 30,  // 30% постов
        commentsTotal: 1500,
        commentsProcessed: 450, // 30% комментариев
        estimatedCommentsPerPost: 15
      };

      const result = ProgressCalculator.calculateProgress(metrics);

      // 50% * 10% + 30% * 30% + 30% * 60% = 5% + 9% + 18% = 32%
      expect(result.percentage).toBe(32);
      expect(result.processed).toBe(32);
      expect(result.total).toBe(100);

      // Никогда не превышает 100%
      expect(result.processed).toBeLessThanOrEqual(100);
    });
  });
});