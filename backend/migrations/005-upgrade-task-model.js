/**
 * Миграция для безопасного обновления модели Task
 * - Преобразование JSON полей в JSONB для лучшей производительности PostgreSQL
 * - Добавление новых полей для расширенной функциональности
 * - Создание ENUM типов для status и type
 * - Безопасное сохранение существующих данных
 */
module.exports = {
  up: async (queryInterface, Sequelize) => {
    const transaction = await queryInterface.sequelize.transaction();

    try {
      // 1. Создаем ENUM типы для статуса и типа задач
      await queryInterface.sequelize.query(`
        DO $$
        BEGIN
          -- Создаем ENUM для статуса задач, если он не существует
          IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'enum_tasks_status') THEN
            CREATE TYPE enum_tasks_status AS ENUM ('pending', 'processing', 'completed', 'failed');
          END IF;

          -- Создаем ENUM для типа задач, если он не существует
          IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'enum_tasks_type') THEN
            CREATE TYPE enum_tasks_type AS ENUM ('fetch_comments', 'process_groups', 'analyze_posts');
          END IF;
        END
        $$;
      `, { transaction });

      // 2. Добавляем новые столбцы с временными именами, чтобы избежать конфликтов

      // Добавляем тип задачи
      await queryInterface.addColumn('tasks', 'type', {
        type: Sequelize.ENUM('fetch_comments', 'process_groups', 'analyze_posts'),
        allowNull: false,
        defaultValue: 'fetch_comments'
      }, { transaction });

      // Добавляем приоритет
      await queryInterface.addColumn('tasks', 'priority', {
        type: Sequelize.INTEGER,
        allowNull: false,
        defaultValue: 0
      }, { transaction });

      // Добавляем прогресс выполнения
      await queryInterface.addColumn('tasks', 'progress', {
        type: Sequelize.INTEGER,
        allowNull: false,
        defaultValue: 0
      }, { transaction });

      // Добавляем параметры конфигурации
      await queryInterface.addColumn('tasks', 'parameters', {
        type: Sequelize.JSONB,
        allowNull: true,
        defaultValue: null
      }, { transaction });

      // Добавляем результат выполнения
      await queryInterface.addColumn('tasks', 'result', {
        type: Sequelize.JSONB,
        allowNull: true,
        defaultValue: null
      }, { transaction });

      // Добавляем ошибки
      await queryInterface.addColumn('tasks', 'error', {
        type: Sequelize.TEXT,
        allowNull: true,
        defaultValue: null
      }, { transaction });

      // Добавляем время выполнения
      await queryInterface.addColumn('tasks', 'executionTime', {
        type: Sequelize.INTEGER,
        allowNull: true,
        defaultValue: null
      }, { transaction });

      // Добавляем создателя задачи
      await queryInterface.addColumn('tasks', 'createdBy', {
        type: Sequelize.STRING(100),
        allowNull: true,
        defaultValue: 'system'
      }, { transaction });

      // 3. Создаем временные JSONB колонки
      await queryInterface.addColumn('tasks', 'groups_temp', {
        type: Sequelize.JSONB,
        allowNull: true,
        defaultValue: null
      }, { transaction });

      await queryInterface.addColumn('tasks', 'metrics_temp', {
        type: Sequelize.JSONB,
        allowNull: true,
        defaultValue: null
      }, { transaction });

      // 4. Конвертируем существующие JSON данные в JSONB
      // Копируем данные из старых JSON колонок в новые JSONB колонки
      await queryInterface.sequelize.query(`
        UPDATE tasks
        SET
          groups_temp = CASE
            WHEN groups IS NOT NULL THEN groups::jsonb
            ELSE NULL
          END,
          metrics_temp = CASE
            WHEN metrics IS NOT NULL THEN metrics::jsonb
            ELSE NULL
          END
        WHERE groups IS NOT NULL OR metrics IS NOT NULL;
      `, { transaction });

      // 5. Удаляем старые JSON колонки
      await queryInterface.removeColumn('tasks', 'groups', { transaction });
      await queryInterface.removeColumn('tasks', 'metrics', { transaction });

      // 6. Переименовываем временные колонки
      await queryInterface.renameColumn('tasks', 'groups_temp', 'groups', { transaction });
      await queryInterface.renameColumn('tasks', 'metrics_temp', 'metrics', { transaction });

      // 7. Создаем временную ENUM колонку для статуса
      await queryInterface.addColumn('tasks', 'status_temp', {
        type: Sequelize.ENUM('pending', 'processing', 'completed', 'failed'),
        allowNull: false,
        defaultValue: 'pending'
      }, { transaction });

      // 8. Конвертируем существующие статусы в ENUM
      await queryInterface.sequelize.query(`
        UPDATE tasks
        SET status_temp = CASE
          WHEN status IN ('pending', 'processing', 'completed', 'failed') THEN status::enum_tasks_status
          ELSE 'pending'::enum_tasks_status
        END;
      `, { transaction });

      // 9. Удаляем старую STRING колонку статуса
      await queryInterface.removeColumn('tasks', 'status', { transaction });

      // 10. Переименовываем временную колонку
      await queryInterface.renameColumn('tasks', 'status_temp', 'status', { transaction });

      await transaction.commit();
      console.log('✅ Миграция задач успешно завершена');

    } catch (error) {
      await transaction.rollback();
      console.error('❌ Ошибка при выполнении миграции задач:', error);
      throw error;
    }
  },

  down: async (queryInterface, Sequelize) => {
    const transaction = await queryInterface.sequelize.transaction();

    try {
      console.log('🔄 Откат миграции задач...');

      // 1. Создаем временные колонки для отката
      await queryInterface.addColumn('tasks', 'status_temp', {
        type: Sequelize.STRING,
        allowNull: false,
        defaultValue: 'pending'
      }, { transaction });

      await queryInterface.addColumn('tasks', 'groups_temp', {
        type: Sequelize.JSON,
        allowNull: true
      }, { transaction });

      await queryInterface.addColumn('tasks', 'metrics_temp', {
        type: Sequelize.JSON,
        allowNull: true
      }, { transaction });

      // 2. Конвертируем данные обратно
      await queryInterface.sequelize.query(`
        UPDATE tasks
        SET
          status_temp = status::text,
          groups_temp = groups::json,
          metrics_temp = metrics::json;
      `, { transaction });

      // 3. Удаляем ENUM колонки и новые поля
      await queryInterface.removeColumn('tasks', 'status', { transaction });
      await queryInterface.removeColumn('tasks', 'groups', { transaction });
      await queryInterface.removeColumn('tasks', 'metrics', { transaction });
      await queryInterface.removeColumn('tasks', 'type', { transaction });
      await queryInterface.removeColumn('tasks', 'priority', { transaction });
      await queryInterface.removeColumn('tasks', 'progress', { transaction });
      await queryInterface.removeColumn('tasks', 'parameters', { transaction });
      await queryInterface.removeColumn('tasks', 'result', { transaction });
      await queryInterface.removeColumn('tasks', 'error', { transaction });
      await queryInterface.removeColumn('tasks', 'executionTime', { transaction });
      await queryInterface.removeColumn('tasks', 'createdBy', { transaction });

      // 4. Переименовываем временные колонки обратно
      await queryInterface.renameColumn('tasks', 'status_temp', 'status', { transaction });
      await queryInterface.renameColumn('tasks', 'groups_temp', 'groups', { transaction });
      await queryInterface.renameColumn('tasks', 'metrics_temp', 'metrics', { transaction });

      // 5. Удаляем ENUM типы
      await queryInterface.sequelize.query(`
        DROP TYPE IF EXISTS enum_tasks_status CASCADE;
        DROP TYPE IF EXISTS enum_tasks_type CASCADE;
      `, { transaction });

      await transaction.commit();
      console.log('✅ Откат миграции задач успешно завершен');

    } catch (error) {
      await transaction.rollback();
      console.error('❌ Ошибка при откате миграции задач:', error);
      throw error;
    }
  }
};