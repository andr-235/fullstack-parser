/**
 * Миграция для создания производительных индексов
 * Оптимизирует запросы к базе данных VK аналитики
 */
module.exports = {
  up: async (queryInterface, Sequelize) => {
    const transaction = await queryInterface.sequelize.transaction();

    try {
      console.log('🚀 Создание производительных индексов...');

      // === ИНДЕКСЫ ДЛЯ ТАБЛИЦЫ TASKS ===

      // 1. Индекс для поиска задач по статусу (часто используется в интерфейсе)
      await queryInterface.addIndex('tasks', {
        fields: ['status'],
        name: 'idx_tasks_status',
        using: 'btree'
      }, { transaction });

      // 2. Составной индекс для приоритизации задач (status + priority + createdAt)
      await queryInterface.addIndex('tasks', {
        fields: ['status', 'priority', 'createdAt'],
        name: 'idx_tasks_priority_queue',
        using: 'btree'
      }, { transaction });

      // 3. Индекс для поиска по типу задач
      await queryInterface.addIndex('tasks', {
        fields: ['type'],
        name: 'idx_tasks_type',
        using: 'btree'
      }, { transaction });

      // 4. Составной индекс для мониторинга активных задач (type + status)
      await queryInterface.addIndex('tasks', {
        fields: ['type', 'status'],
        name: 'idx_tasks_type_status',
        using: 'btree'
      }, { transaction });

      // 5. Индекс для временных запросов (часто нужна сортировка по времени создания)
      await queryInterface.addIndex('tasks', {
        fields: ['createdAt'],
        name: 'idx_tasks_created_at',
        using: 'btree'
      }, { transaction });

      // 6. Частичный индекс для активных задач (экономит место)
      await queryInterface.sequelize.query(`
        CREATE INDEX CONCURRENTLY idx_tasks_active
        ON tasks (id, "createdAt")
        WHERE status IN ('pending', 'processing');
      `, { transaction });

      // === ИНДЕКСЫ ДЛЯ ТАБЛИЦЫ POSTS ===

      // 7. Уникальный индекс для VK post ID (предотвращает дубликаты)
      await queryInterface.addIndex('posts', {
        fields: ['vk_post_id'],
        name: 'idx_posts_vk_id_unique',
        unique: true,
        using: 'btree'
      }, { transaction });

      // 8. Индекс для поиска постов по группе
      await queryInterface.addIndex('posts', {
        fields: ['group_id'],
        name: 'idx_posts_group_id',
        using: 'btree'
      }, { transaction });

      // 9. Составной индекс для фильтрации по задаче + дате
      await queryInterface.addIndex('posts', {
        fields: ['taskId', 'date'],
        name: 'idx_posts_task_date',
        using: 'btree'
      }, { transaction });

      // 10. Индекс для поиска по владельцу
      await queryInterface.addIndex('posts', {
        fields: ['owner_id'],
        name: 'idx_posts_owner_id',
        using: 'btree'
      }, { transaction });

      // === ИНДЕКСЫ ДЛЯ ТАБЛИЦЫ COMMENTS ===

      // 11. Уникальный индекс для VK comment ID
      await queryInterface.addIndex('comments', {
        fields: ['vk_comment_id'],
        name: 'idx_comments_vk_id_unique',
        unique: true,
        using: 'btree'
      }, { transaction });

      // 12. Индекс для связи комментариев с постами
      await queryInterface.addIndex('comments', {
        fields: ['post_vk_id'],
        name: 'idx_comments_post_vk_id',
        using: 'btree'
      }, { transaction });

      // 13. Индекс для поиска по автору комментария
      await queryInterface.addIndex('comments', {
        fields: ['author_id'],
        name: 'idx_comments_author_id',
        using: 'btree'
      }, { transaction });

      // 14. Индекс по дате для временной сортировки комментариев
      await queryInterface.addIndex('comments', {
        fields: ['date'],
        name: 'idx_comments_date',
        using: 'btree'
      }, { transaction });

      // 15. Составной индекс для пагинации комментариев (post + date)
      await queryInterface.addIndex('comments', {
        fields: ['post_vk_id', 'date'],
        name: 'idx_comments_post_date',
        using: 'btree'
      }, { transaction });

      // 16. Полнотекстовый индекс для поиска по тексту комментариев (PostgreSQL GIN)
      await queryInterface.sequelize.query(`
        CREATE INDEX CONCURRENTLY idx_comments_fulltext
        ON comments USING gin(to_tsvector('russian', text));
      `, { transaction });

      // === ИНДЕКСЫ ДЛЯ ТАБЛИЦЫ GROUPS ===

      // 17. Составной индекс для поиска групп (предполагаем существование таблицы groups)
      const tablesResult = await queryInterface.sequelize.query(`
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'groups';
      `, { transaction });

      if (tablesResult[0].length > 0) {
        // Проверяем какие колонки есть в таблице groups
        const columnsResult = await queryInterface.sequelize.query(`
          SELECT column_name
          FROM information_schema.columns
          WHERE table_name = 'groups' AND table_schema = 'public';
        `, { transaction });

        const columnNames = columnsResult[0].map(row => row.column_name);

        // Создаем индексы только если колонки существуют
        if (columnNames.includes('vk_group_id')) {
          await queryInterface.addIndex('groups', {
            fields: ['vk_group_id'],
            name: 'idx_groups_vk_id',
            unique: true,
            using: 'btree'
          }, { transaction });
        }

        if (columnNames.includes('name')) {
          await queryInterface.addIndex('groups', {
            fields: ['name'],
            name: 'idx_groups_name',
            using: 'btree'
          }, { transaction });
        }

        if (columnNames.includes('is_active')) {
          // Частичный индекс для активных групп
          await queryInterface.sequelize.query(`
            CREATE INDEX CONCURRENTLY idx_groups_active
            ON groups (id, name)
            WHERE is_active = true;
          `, { transaction });
        }
      }

      // === СТАТИСТИКА ИНДЕКСОВ ===

      // Обновляем статистику PostgreSQL для оптимального планирования запросов
      await queryInterface.sequelize.query('ANALYZE;', { transaction });

      await transaction.commit();
      console.log('✅ Все производительные индексы успешно созданы');

    } catch (error) {
      await transaction.rollback();
      console.error('❌ Ошибка при создании индексов:', error);
      throw error;
    }
  },

  down: async (queryInterface, Sequelize) => {
    const transaction = await queryInterface.sequelize.transaction();

    try {
      console.log('🔄 Удаление производительных индексов...');

      // Список всех индексов для удаления
      const indexesToDrop = [
        'idx_tasks_status',
        'idx_tasks_priority_queue',
        'idx_tasks_type',
        'idx_tasks_type_status',
        'idx_tasks_created_at',
        'idx_tasks_active',
        'idx_posts_vk_id_unique',
        'idx_posts_group_id',
        'idx_posts_task_date',
        'idx_posts_owner_id',
        'idx_comments_vk_id_unique',
        'idx_comments_post_vk_id',
        'idx_comments_author_id',
        'idx_comments_date',
        'idx_comments_post_date',
        'idx_comments_fulltext',
        'idx_groups_vk_id',
        'idx_groups_name',
        'idx_groups_active'
      ];

      // Удаляем каждый индекс, игнорируя ошибки если индекс не существует
      for (const indexName of indexesToDrop) {
        try {
          await queryInterface.sequelize.query(`DROP INDEX IF EXISTS ${indexName};`, { transaction });
        } catch (error) {
          console.warn(`⚠️ Не удалось удалить индекс ${indexName}:`, error.message);
        }
      }

      await transaction.commit();
      console.log('✅ Индексы успешно удалены');

    } catch (error) {
      await transaction.rollback();
      console.error('❌ Ошибка при удалении индексов:', error);
      throw error;
    }
  }
};