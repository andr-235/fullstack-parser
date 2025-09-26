/**
 * Утилита для мониторинга производительности PostgreSQL базы данных
 * Предоставляет методы для анализа производительности, статистики и оптимизации
 */

import { Sequelize, QueryTypes } from 'sequelize';
import logger from './logger';

interface PoolStats {
  size: number;
  available: number;
  using: number;
  waiting: number;
  max: number;
  min: number;
}

interface SlowQuery {
  query: string;
  calls: number;
  total_time: number;
  mean_time: number;
  min_time: number;
  max_time: number;
  stddev_time: number;
  rows: number;
}

interface IndexUsage {
  schemaname: string;
  tablename: string;
  indexname: string;
  idx_tup_read: number;
  idx_tup_fetch: number;
  idx_scan: number;
  usage_status: string;
}

interface TableSize {
  schemaname: string;
  tablename: string;
  total_size: string;
  table_size: string;
  indexes_size: string;
  total_bytes: number;
}

interface TableActivity {
  schemaname: string;
  tablename: string;
  inserts: number;
  updates: number;
  deletes: number;
  hot_updates: number;
  seq_scan: number;
  seq_tup_read: number;
  idx_scan: number;
  idx_tup_fetch: number;
  live_tuples: number;
  dead_tuples: number;
  last_vacuum: Date | null;
  last_autovacuum: Date | null;
  last_analyze: Date | null;
  last_autoanalyze: Date | null;
}

interface ActiveConnection {
  pid: number;
  usename: string;
  application_name: string;
  client_addr: string;
  state: string;
  query_start: Date;
  state_change: Date;
  current_query: string;
}

interface BlockingQuery {
  blocked_pid: number;
  blocked_user: string;
  blocking_pid: number;
  blocking_user: string;
  blocked_statement: string;
  blocking_statement: string;
  blocked_application: string;
  blocking_application: string;
}

interface OptimizationRecommendation {
  type: 'unused_indexes' | 'vacuum_needed' | 'large_tables' | 'connection_pool';
  priority: 'low' | 'medium' | 'high' | 'info';
  description: string;
  details: string[];
  suggestion: string;
}

interface HealthCheck {
  timestamp: Date;
  database: string;
  status: 'healthy' | 'warning' | 'critical' | 'error';
  connection?: 'ok' | 'error';
  poolStats?: PoolStats;
  tableSizes?: TableSize[];
  activeConnections?: number;
  blockingQueries?: number;
  recommendations?: OptimizationRecommendation[];
  error?: string;
}

interface BenchmarkResult {
  operation: string;
  duration: number;
}

interface Benchmark {
  timestamp: Date;
  results: BenchmarkResult[];
  averageLatency: number;
}

class DatabaseMonitor {
  private sequelize: Sequelize;

  constructor(sequelize: Sequelize) {
    this.sequelize = sequelize;
  }

  /**
   * Получить статистику использования connection pool
   */
  async getPoolStats(): Promise<PoolStats> {
    const pool = (this.sequelize.connectionManager as any).pool;
    return {
      size: pool.size || 0,
      available: pool.available || 0,
      using: pool.using || 0,
      waiting: pool.waiting || 0,
      max: pool.max || 0,
      min: pool.min || 0
    };
  }

  /**
   * Анализ медленных запросов
   */
  async getSlowQueries(limit = 10): Promise<SlowQuery[]> {
    const query = `
      SELECT
        query,
        calls,
        total_time,
        mean_time,
        min_time,
        max_time,
        stddev_time,
        rows
      FROM pg_stat_statements
      WHERE calls > 1
      ORDER BY mean_time DESC
      LIMIT :limit;
    `;

    try {
      const results = await this.sequelize.query(query, {
        replacements: { limit },
        type: QueryTypes.SELECT
      }) as SlowQuery[];
      return results;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.warn('pg_stat_statements extension не активирована', { error: errorMsg });
      return [];
    }
  }

  /**
   * Анализ использования индексов
   */
  async getIndexUsage(tableName?: string): Promise<IndexUsage[]> {
    const whereClause = tableName ? 'AND schemaname = :schema AND tablename = :tableName' : '';
    const query = `
      SELECT
        schemaname,
        tablename,
        indexname,
        idx_tup_read,
        idx_tup_fetch,
        idx_scan,
        CASE
          WHEN idx_scan = 0 THEN 'Never used'
          WHEN idx_scan < 10 THEN 'Rarely used'
          ELSE 'Actively used'
        END as usage_status
      FROM pg_stat_user_indexes
      WHERE schemaname = 'public' ${whereClause}
      ORDER BY idx_scan DESC;
    `;

    const results = await this.sequelize.query(query, {
      replacements: { schema: 'public', tableName },
      type: QueryTypes.SELECT
    }) as IndexUsage[];
    return results;
  }

  /**
   * Размеры таблиц и индексов
   */
  async getTableSizes(): Promise<TableSize[]> {
    const query = `
      SELECT
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
        pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
        pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size,
        pg_total_relation_size(schemaname||'.'||tablename) AS total_bytes
      FROM pg_tables
      WHERE schemaname = 'public'
      ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    `;

    const results = await this.sequelize.query(query, {
      type: QueryTypes.SELECT
    }) as TableSize[];
    return results;
  }

  /**
   * Статистика активности таблиц
   */
  async getTableActivity(): Promise<TableActivity[]> {
    const query = `
      SELECT
        schemaname,
        tablename,
        n_tup_ins as inserts,
        n_tup_upd as updates,
        n_tup_del as deletes,
        n_tup_hot_upd as hot_updates,
        seq_scan,
        seq_tup_read,
        idx_scan,
        idx_tup_fetch,
        n_live_tup as live_tuples,
        n_dead_tup as dead_tuples,
        last_vacuum,
        last_autovacuum,
        last_analyze,
        last_autoanalyze
      FROM pg_stat_user_tables
      WHERE schemaname = 'public'
      ORDER BY (n_tup_ins + n_tup_upd + n_tup_del) DESC;
    `;

    const results = await this.sequelize.query(query, {
      type: QueryTypes.SELECT
    }) as TableActivity[];
    return results;
  }

  /**
   * Активные соединения и блокировки
   */
  async getActiveConnections(): Promise<ActiveConnection[]> {
    const query = `
      SELECT
        pid,
        usename,
        application_name,
        client_addr,
        state,
        query_start,
        state_change,
        CASE
          WHEN state = 'active' THEN query
          ELSE 'Not active'
        END as current_query
      FROM pg_stat_activity
      WHERE datname = current_database()
        AND pid <> pg_backend_pid()
      ORDER BY query_start DESC;
    `;

    const results = await this.sequelize.query(query, {
      type: QueryTypes.SELECT
    }) as ActiveConnection[];
    return results;
  }

  /**
   * Детектор блокировок
   */
  async getBlockingQueries(): Promise<BlockingQuery[]> {
    const query = `
      SELECT
        blocked_locks.pid AS blocked_pid,
        blocked_activity.usename AS blocked_user,
        blocking_locks.pid AS blocking_pid,
        blocking_activity.usename AS blocking_user,
        blocked_activity.query AS blocked_statement,
        blocking_activity.query AS blocking_statement,
        blocked_activity.application_name AS blocked_application,
        blocking_activity.application_name AS blocking_application
      FROM pg_catalog.pg_locks blocked_locks
      JOIN pg_catalog.pg_stat_activity blocked_activity
        ON blocked_activity.pid = blocked_locks.pid
      JOIN pg_catalog.pg_locks blocking_locks
        ON blocking_locks.locktype = blocked_locks.locktype
        AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE
        AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
        AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
        AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
        AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
        AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
        AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
        AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
        AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
        AND blocking_locks.pid != blocked_locks.pid
      JOIN pg_catalog.pg_stat_activity blocking_activity
        ON blocking_activity.pid = blocking_locks.pid
      WHERE NOT blocked_locks.GRANTED;
    `;

    const results = await this.sequelize.query(query, {
      type: QueryTypes.SELECT
    }) as BlockingQuery[];
    return results;
  }

  /**
   * Рекомендации по оптимизации
   */
  async getOptimizationRecommendations(): Promise<OptimizationRecommendation[]> {
    const recommendations: OptimizationRecommendation[] = [];

    // 1. Проверяем неиспользуемые индексы
    const indexUsage = await this.getIndexUsage();
    const unusedIndexes = indexUsage.filter(idx =>
      idx.usage_status === 'Never used' && !idx.indexname.endsWith('_pkey')
    );

    if (unusedIndexes.length > 0) {
      recommendations.push({
        type: 'unused_indexes',
        priority: 'medium',
        description: `Обнаружено ${unusedIndexes.length} неиспользуемых индексов`,
        details: unusedIndexes.map(idx => `${idx.tablename}.${idx.indexname}`),
        suggestion: 'Рассмотрите удаление неиспользуемых индексов для экономии места'
      });
    }

    // 2. Проверяем таблицы с большим количеством мертвых кортежей
    const tableActivity = await this.getTableActivity();
    const needVacuum = tableActivity.filter(table =>
      table.dead_tuples > 1000 &&
      table.dead_tuples / (table.live_tuples || 1) > 0.1
    );

    if (needVacuum.length > 0) {
      recommendations.push({
        type: 'vacuum_needed',
        priority: 'high',
        description: `${needVacuum.length} таблиц нуждаются в VACUUM`,
        details: needVacuum.map(table => `${table.tablename} (${table.dead_tuples} мертвых записей)`),
        suggestion: 'Запустите VACUUM ANALYZE для оптимизации производительности'
      });
    }

    // 3. Проверяем размеры таблиц
    const tableSizes = await this.getTableSizes();
    const largeTables = tableSizes.filter(table => table.total_bytes > 100 * 1024 * 1024); // > 100MB

    if (largeTables.length > 0) {
      recommendations.push({
        type: 'large_tables',
        priority: 'info',
        description: `Найдены крупные таблицы (>${tableSizes[0]?.total_size})`,
        details: largeTables.map(table => `${table.tablename}: ${table.total_size}`),
        suggestion: 'Рассмотрите партиционирование или архивирование старых данных'
      });
    }

    // 4. Проверяем connection pool
    const poolStats = await this.getPoolStats();
    if (poolStats.max > 0 && poolStats.using / poolStats.max > 0.8) {
      recommendations.push({
        type: 'connection_pool',
        priority: 'medium',
        description: 'Высокая загрузка connection pool',
        details: [`Используется ${poolStats.using}/${poolStats.max} соединений`],
        suggestion: 'Рассмотрите увеличение размера пула или оптимизацию запросов'
      });
    }

    return recommendations;
  }

  /**
   * Комплексная проверка здоровья базы данных
   */
  async healthCheck(): Promise<HealthCheck> {
    const health: HealthCheck = {
      timestamp: new Date(),
      database: this.sequelize.getDatabaseName(),
      status: 'healthy'
    };

    try {
      // Проверяем подключение
      await this.sequelize.authenticate();
      health.connection = 'ok';

      // Получаем основные метрики
      health.poolStats = await this.getPoolStats();
      health.tableSizes = await this.getTableSizes();
      health.activeConnections = (await this.getActiveConnections()).length;
      health.blockingQueries = (await this.getBlockingQueries()).length;
      health.recommendations = await this.getOptimizationRecommendations();

      // Определяем общий статус здоровья
      const highPriorityIssues = health.recommendations.filter(r => r.priority === 'high');
      if (highPriorityIssues.length > 0) {
        health.status = 'warning';
      }

      if (health.blockingQueries > 0) {
        health.status = 'critical';
      }

    } catch (error) {
      health.status = 'error';
      health.error = error instanceof Error ? error.message : String(error);
    }

    return health;
  }

  /**
   * Выполнение EXPLAIN ANALYZE для запроса
   */
  async explainQuery(query: string, params: Record<string, any> = {}): Promise<any> {
    const explainQuery = `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) ${query}`;

    try {
      const results = await this.sequelize.query(explainQuery, {
        replacements: params,
        type: QueryTypes.SELECT
      });
      return results[0];
    } catch (error) {
      logger.error('Ошибка при выполнении EXPLAIN', { error });
      throw error;
    }
  }

  /**
   * Бенчмарк для типичных запросов VK аналитики
   */
  async runBenchmark(): Promise<Benchmark> {
    const benchmarks: BenchmarkResult[] = [];

    try {
      // 1. Тест создания задачи
      const taskCreateStart = Date.now();
      await this.sequelize.query(`
        INSERT INTO tasks (status, type, priority, progress, "createdAt", "updatedAt")
        VALUES ('pending', 'fetch_comments', 1, 0, NOW(), NOW())
      `);
      benchmarks.push({
        operation: 'create_task',
        duration: Date.now() - taskCreateStart
      });

      // 2. Тест поиска задач по статусу
      const taskSearchStart = Date.now();
      await this.sequelize.query(`
        SELECT * FROM tasks WHERE status = 'pending' ORDER BY priority DESC, "createdAt" ASC LIMIT 10
      `);
      benchmarks.push({
        operation: 'search_pending_tasks',
        duration: Date.now() - taskSearchStart
      });

      // 3. Тест поиска комментариев с join
      const commentsSearchStart = Date.now();
      await this.sequelize.query(`
        SELECT c.*, p.text as post_text
        FROM comments c
        JOIN posts p ON c.post_vk_id = p.vk_post_id
        WHERE c.date >= NOW() - INTERVAL '7 days'
        ORDER BY c.date DESC
        LIMIT 100
      `);
      benchmarks.push({
        operation: 'search_recent_comments_with_posts',
        duration: Date.now() - commentsSearchStart
      });
    } catch (error) {
      logger.error('Benchmark execution failed', { error });
    }

    return {
      timestamp: new Date(),
      results: benchmarks,
      averageLatency: benchmarks.length > 0
        ? benchmarks.reduce((sum, b) => sum + b.duration, 0) / benchmarks.length
        : 0
    };
  }
}

export default DatabaseMonitor;
export { DatabaseMonitor };
export type {
  PoolStats,
  SlowQuery,
  IndexUsage,
  TableSize,
  TableActivity,
  ActiveConnection,
  BlockingQuery,
  OptimizationRecommendation,
  HealthCheck,
  BenchmarkResult,
  Benchmark
};