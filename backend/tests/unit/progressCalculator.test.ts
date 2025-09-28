import { ProgressCalculator } from '@/services/progressCalculator';
import { TaskMetrics } from '@/types/task';

describe('ProgressCalculator', () => {
  describe('calculateProgress', () => {
    it('должен корректно рассчитывать прогресс начальной фазы (groups)', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 10,
        groupsProcessed: 5,
        postsTotal: 0,
        postsProcessed: 0,
        commentsTotal: 0,
        commentsProcessed: 0,
        estimatedCommentsPerPost: 15
      };

      const result = ProgressCalculator.calculateProgress(metrics);

      expect(result.phase).toBe('groups');
      expect(result.percentage).toBe(5); // 50% от 10% (weight группы)
      expect(result.processed).toBe(5);
      expect(result.total).toBe(100);
      expect(result.phases.groups.progress).toBe(0.5);
      expect(result.phases.groups.completed).toBe(false);
    });

    it('должен переходить в фазу posts после завершения groups', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 10,
        groupsProcessed: 10,
        postsTotal: 50,
        postsProcessed: 25,
        commentsTotal: 0,
        commentsProcessed: 0,
        estimatedCommentsPerPost: 15
      };

      const result = ProgressCalculator.calculateProgress(metrics);

      expect(result.phase).toBe('posts');
      expect(result.phases.groups.completed).toBe(true);
      expect(result.phases.posts.progress).toBe(0.5); // 50% постов обработано
      expect(result.percentage).toBe(25); // 10% (groups) + 15% (50% от 30% posts)
    });

    it('должен переходить в фазу comments после завершения posts', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 10,
        groupsProcessed: 10,
        postsTotal: 50,
        postsProcessed: 50,
        commentsTotal: 750, // 50 * 15
        commentsProcessed: 375,
        estimatedCommentsPerPost: 15
      };

      const result = ProgressCalculator.calculateProgress(metrics);

      expect(result.phase).toBe('comments');
      expect(result.phases.groups.completed).toBe(true);
      expect(result.phases.posts.completed).toBe(true);
      expect(result.phases.comments.progress).toBe(0.5); // 50% комментариев
      expect(result.percentage).toBe(70); // 10% + 30% + 30% (50% от 60% comments)
    });

    it('должен использовать оценочный прогресс для комментариев при отсутствии точного total', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 5,
        groupsProcessed: 5,
        postsTotal: 25,
        postsProcessed: 25,
        commentsTotal: 0, // Нет точного значения
        commentsProcessed: 150,
        estimatedCommentsPerPost: 15
      };

      const result = ProgressCalculator.calculateProgress(metrics);

      expect(result.phase).toBe('comments');
      // Ожидаемые комментарии: 25 * 15 = 375
      // Прогресс: 150 / 375 = 0.4
      expect(result.phases.comments.progress).toBeCloseTo(0.4, 2);
    });

    it('не должен превышать 100% прогресса', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 5,
        groupsProcessed: 10, // Больше чем total (некорректные данные)
        postsTotal: 25,
        postsProcessed: 50, // Больше чем total
        commentsTotal: 375,
        commentsProcessed: 1000, // Больше чем total
        estimatedCommentsPerPost: 15
      };

      const result = ProgressCalculator.calculateProgress(metrics);

      expect(result.percentage).toBeLessThanOrEqual(100);
      expect(result.processed).toBeLessThanOrEqual(100);
    });

    it('должен корректно обрабатывать нулевые значения', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 0,
        groupsProcessed: 0,
        postsTotal: 0,
        postsProcessed: 0,
        commentsTotal: 0,
        commentsProcessed: 0,
        estimatedCommentsPerPost: 15
      };

      const result = ProgressCalculator.calculateProgress(metrics);

      expect(result.percentage).toBe(0);
      expect(result.phase).toBe('groups');
      expect(result.phases.groups.progress).toBe(0);
      expect(result.phases.posts.progress).toBe(0);
      expect(result.phases.comments.progress).toBe(0);
    });
  });

  describe('estimateTotal', () => {
    it('должен рассчитывать оценку на основе количества групп', () => {
      const taskData = {
        groups: [{ id: 1, name: 'Group 1' }, { id: 2, name: 'Group 2' }]
      };

      const estimate = ProgressCalculator.estimateTotal(taskData);

      // 2 группы * 50 постов * 15 комментариев = 1500
      expect(estimate).toBe(1500);
    });

    it('должен учитывать ограничение maxComments', () => {
      const taskData = {
        groups: [{ id: 1 }, { id: 2 }],
        maxComments: 500
      };

      const estimate = ProgressCalculator.estimateTotal(taskData);

      expect(estimate).toBe(500); // Ограничено maxComments
    });

    it('должен использовать минимальное значение по умолчанию', () => {
      const taskData = {
        groups: []
      };

      const estimate = ProgressCalculator.estimateTotal(taskData);

      expect(estimate).toBe(100); // Минимальное значение по умолчанию
    });
  });

  describe('validateMetrics', () => {
    it('должен выявлять ошибку когда processed > total', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 5,
        groupsProcessed: 10, // Больше total
        postsTotal: 25,
        postsProcessed: 20,
        commentsTotal: 375,
        commentsProcessed: 300,
        estimatedCommentsPerPost: 15
      };

      const errors = ProgressCalculator.validateMetrics(metrics);

      expect(errors).toHaveLength(1);
      expect(errors[0]).toContain('Groups: processed (10) > total (5)');
    });

    it('должен находить множественные ошибки', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 5,
        groupsProcessed: 10,
        postsTotal: 25,
        postsProcessed: 50,
        commentsTotal: 375,
        commentsProcessed: 1000,
        estimatedCommentsPerPost: 15
      };

      const errors = ProgressCalculator.validateMetrics(metrics);

      expect(errors).toHaveLength(3);
      expect(errors.some(e => e.includes('Groups'))).toBe(true);
      expect(errors.some(e => e.includes('Posts'))).toBe(true);
      expect(errors.some(e => e.includes('Comments'))).toBe(true);
    });

    it('должен возвращать пустой массив для корректных метрик', () => {
      const metrics: TaskMetrics = {
        groupsTotal: 5,
        groupsProcessed: 3,
        postsTotal: 25,
        postsProcessed: 15,
        commentsTotal: 375,
        commentsProcessed: 200,
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
        groups: [{ id: 1 }, { id: 2 }, { id: 3 }],
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