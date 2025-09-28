/**
 * ProgressCalculator - точный расчет прогресса задач VK Analytics
 *
 * Реализует многофазную систему расчета прогресса с весовыми коэффициентами.
 * Устраняет проблему произвольных множителей и ситуацию processed > total.
 */

/**
 * Метрики для расчета прогресса задачи
 */
export interface TaskMetrics {
  /** Общее количество групп для обработки */
  groupsTotal: number;
  /** Количество обработанных групп */
  groupsProcessed: number;
  /** Общее количество постов */
  postsTotal: number;
  /** Количество обработанных постов */
  postsProcessed: number;
  /** Общее количество комментариев (точное или оценочное) */
  commentsTotal: number;
  /** Количество обработанных комментариев */
  commentsProcessed: number;
  /** Среднее количество комментариев на пост для оценки */
  estimatedCommentsPerPost: number;
}

/**
 * Результат расчета прогресса
 */
export interface ProgressResult {
  /** Количество обработанных единиц (в процентах 0-100) */
  processed: number;
  /** Общее количество единиц (всегда 100 для процентной системы) */
  total: number;
  /** Процент выполнения (0-100) */
  percentage: number;
  /** Текущая фаза обработки */
  phase: 'groups' | 'posts' | 'comments';
  /** Детальная информация о каждой фазе */
  phases: {
    groups: { weight: number; progress: number; completed: boolean };
    posts: { weight: number; progress: number; completed: boolean };
    comments: { weight: number; progress: number; completed: boolean };
  };
}

/**
 * Калькулятор прогресса задач с многофазной архитектурой
 */
export class ProgressCalculator {
  /** Весовые коэффициенты для каждой фазы обработки */
  private static readonly PHASE_WEIGHTS = {
    groups: 0.1,      // 10% - получение списка групп и базовой информации
    posts: 0.3,       // 30% - получение постов из групп
    comments: 0.6     // 60% - получение комментариев к постам
  } as const;

  /** Значения по умолчанию для оценки */
  private static readonly DEFAULTS = {
    avgCommentsPerPost: 15,
    avgPostsPerGroup: 50,
    minEstimatedTotal: 100
  } as const;

  /**
   * Основной метод расчета прогресса задачи
   *
   * @param metrics Метрики выполнения задачи
   * @returns Детальная информация о прогрессе
   */
  static calculateProgress(metrics: TaskMetrics): ProgressResult {
    const phases = {
      groups: this.calculateGroupsPhase(metrics),
      posts: this.calculatePostsPhase(metrics),
      comments: this.calculateCommentsPhase(metrics)
    };

    // Определяем текущую фазу
    let currentPhase: 'groups' | 'posts' | 'comments' = 'groups';
    if (phases.groups.completed && phases.posts.progress > 0) {
      currentPhase = 'posts';
    }
    if (phases.posts.completed && phases.comments.progress > 0) {
      currentPhase = 'comments';
    }

    // Суммируем прогресс всех фаз
    const totalProgress =
      phases.groups.weight * phases.groups.progress +
      phases.posts.weight * phases.posts.progress +
      phases.comments.weight * phases.comments.progress;

    const percentage = Math.min(Math.round(totalProgress * 100), 100);

    return {
      processed: percentage,
      total: 100,
      percentage,
      phase: currentPhase,
      phases: {
        groups: phases.groups,
        posts: phases.posts,
        comments: phases.comments
      }
    };
  }

  /**
   * Расчет прогресса фазы обработки групп
   */
  private static calculateGroupsPhase(metrics: TaskMetrics) {
    const progress = metrics.groupsTotal > 0
      ? Math.min(metrics.groupsProcessed / metrics.groupsTotal, 1)
      : 0;

    return {
      weight: this.PHASE_WEIGHTS.groups,
      progress,
      completed: metrics.groupsTotal > 0 && metrics.groupsProcessed >= metrics.groupsTotal
    };
  }

  /**
   * Расчет прогресса фазы получения постов
   */
  private static calculatePostsPhase(metrics: TaskMetrics) {
    let progress = 0;

    if (metrics.postsTotal > 0) {
      progress = Math.min(metrics.postsProcessed / metrics.postsTotal, 1);
    } else if (metrics.groupsProcessed > 0) {
      // Если постов еще нет, но группы обрабатываются - показываем начальный прогресс
      progress = Math.min(metrics.groupsProcessed * 0.1, 0.5);
    }

    return {
      weight: this.PHASE_WEIGHTS.posts,
      progress,
      completed: metrics.postsTotal > 0 && metrics.postsProcessed >= metrics.postsTotal
    };
  }

  /**
   * Расчет прогресса фазы получения комментариев
   */
  private static calculateCommentsPhase(metrics: TaskMetrics) {
    let progress = 0;

    if (metrics.commentsTotal > 0) {
      progress = Math.min(metrics.commentsProcessed / metrics.commentsTotal, 1);
    } else if (metrics.postsProcessed > 0) {
      // Оценочный прогресс на основе обработанных постов
      const estimatedComments = metrics.postsProcessed * metrics.estimatedCommentsPerPost;
      if (estimatedComments > 0) {
        progress = Math.min(metrics.commentsProcessed / estimatedComments, 1);
      }
    }

    return {
      weight: this.PHASE_WEIGHTS.comments,
      progress,
      completed: metrics.commentsTotal > 0 && metrics.commentsProcessed >= metrics.commentsTotal
    };
  }

  /**
   * Оценка общего объема работы на основе входных данных
   *
   * @param taskData Данные задачи
   * @returns Оценочное общее количество комментариев
   */
  static estimateTotal(taskData: {
    groups?: any[];
    groupIds?: number[];
    maxComments?: number;
    options?: { maxComments?: number };
  }): number {
    const groupsCount = taskData.groups?.length || taskData.groupIds?.length || 0;

    // Базовая оценка: группы * посты на группу * комментарии на пост
    const estimatedPosts = groupsCount * this.DEFAULTS.avgPostsPerGroup;
    const estimatedComments = estimatedPosts * this.DEFAULTS.avgCommentsPerPost;

    // Учитываем ограничения если они заданы
    const maxComments = taskData.maxComments || taskData.options?.maxComments;
    if (maxComments && maxComments > 0) {
      return Math.min(estimatedComments, maxComments);
    }

    return Math.max(estimatedComments, this.DEFAULTS.minEstimatedTotal);
  }

  /**
   * Создание метрик из данных задачи для расчета прогресса
   *
   * @param taskStatus Статус задачи из БД
   * @returns Объект метрик для расчета прогресса
   */
  static createMetricsFromTask(taskStatus: any): TaskMetrics {
    const groupsTotal = taskStatus.groupIds?.length || taskStatus.groups?.length || 0;
    const groupsProcessed = taskStatus.groupsProcessed || 0;

    // Метрики постов
    const postsTotal = taskStatus.postsTotal || taskStatus.metrics?.posts || 0;
    const postsProcessed = taskStatus.postsProcessed || taskStatus.metrics?.posts || 0;

    // Метрики комментариев
    const commentsProcessed = taskStatus.metrics?.comments || 0;
    const commentsTotal = taskStatus.commentsTotal || this.estimateTotal(taskStatus);

    return {
      groupsTotal,
      groupsProcessed,
      postsTotal,
      postsProcessed,
      commentsTotal,
      commentsProcessed,
      estimatedCommentsPerPost: this.DEFAULTS.avgCommentsPerPost
    };
  }

  /**
   * Проверка корректности метрик (для отладки и тестирования)
   */
  static validateMetrics(metrics: TaskMetrics): string[] {
    const errors: string[] = [];

    if (metrics.groupsProcessed > metrics.groupsTotal) {
      errors.push(`Groups: processed (${metrics.groupsProcessed}) > total (${metrics.groupsTotal})`);
    }

    if (metrics.postsProcessed > metrics.postsTotal && metrics.postsTotal > 0) {
      errors.push(`Posts: processed (${metrics.postsProcessed}) > total (${metrics.postsTotal})`);
    }

    if (metrics.commentsProcessed > metrics.commentsTotal && metrics.commentsTotal > 0) {
      errors.push(`Comments: processed (${metrics.commentsProcessed}) > total (${metrics.commentsTotal})`);
    }

    return errors;
  }
}