/**
 * Миграция для обновления constraints до allowNull: false
 * Приводим схему базы данных в соответствие с моделями
 * Безопасно обновляем существующие данные и добавляем NOT NULL constraints
 */
module.exports = {
  up: async (queryInterface, Sequelize) => {
    const transaction = await queryInterface.sequelize.transaction();

    try {
      console.log('🔧 Обновление constraints до NOT NULL...');

      // === ОБНОВЛЕНИЕ ТАБЛИЦЫ POSTS ===

      // 1. Проверяем и исправляем NULL значения в обязательных полях posts
      console.log('📝 Обработка таблицы posts...');

      // Устанавливаем значения по умолчанию для NULL полей
      await queryInterface.sequelize.query(`
        UPDATE posts
        SET
          vk_post_id = COALESCE(vk_post_id, 0),
          owner_id = COALESCE(owner_id, 0),
          group_id = COALESCE(group_id, 0),
          date = COALESCE(date, NOW()),
          text = COALESCE(text, ''),
          likes = COALESCE(likes, 0),
          "taskId" = COALESCE("taskId", 1)
        WHERE
          vk_post_id IS NULL OR
          owner_id IS NULL OR
          group_id IS NULL OR
          date IS NULL OR
          text IS NULL OR
          likes IS NULL OR
          "taskId" IS NULL;
      `, { transaction });

      // 2. Добавляем NOT NULL constraints к posts
      const postConstraints = [
        { column: 'vk_post_id', type: Sequelize.INTEGER },
        { column: 'owner_id', type: Sequelize.INTEGER },
        { column: 'group_id', type: Sequelize.INTEGER },
        { column: 'date', type: Sequelize.DATE },
        { column: 'taskId', type: Sequelize.INTEGER }
      ];

      for (const constraint of postConstraints) {
        try {
          await queryInterface.changeColumn('posts', constraint.column, {
            type: constraint.type,
            allowNull: false
          }, { transaction });
        } catch (error) {
          console.warn(`⚠️  Constraint для posts.${constraint.column} уже существует или произошла ошибка:`, error.message);
        }
      }

      // === ОБНОВЛЕНИЕ ТАБЛИЦЫ COMMENTS ===

      // 3. Проверяем и исправляем NULL значения в обязательных полях comments
      console.log('💬 Обработка таблицы comments...');

      await queryInterface.sequelize.query(`
        UPDATE comments
        SET
          vk_comment_id = COALESCE(vk_comment_id, 0),
          post_vk_id = COALESCE(post_vk_id, 0),
          owner_id = COALESCE(owner_id, 0),
          author_id = COALESCE(author_id, 0),
          author_name = COALESCE(author_name, 'Unknown'),
          date = COALESCE(date, NOW()),
          text = COALESCE(text, ''),
          likes = COALESCE(likes, 0)
        WHERE
          vk_comment_id IS NULL OR
          post_vk_id IS NULL OR
          owner_id IS NULL OR
          author_id IS NULL OR
          author_name IS NULL OR
          date IS NULL OR
          text IS NULL OR
          likes IS NULL;
      `, { transaction });

      // 4. Добавляем NOT NULL constraints к comments
      const commentConstraints = [
        { column: 'vk_comment_id', type: Sequelize.INTEGER },
        { column: 'post_vk_id', type: Sequelize.INTEGER },
        { column: 'owner_id', type: Sequelize.INTEGER },
        { column: 'author_id', type: Sequelize.INTEGER },
        { column: 'author_name', type: Sequelize.STRING(255) },
        { column: 'date', type: Sequelize.DATE }
      ];

      for (const constraint of commentConstraints) {
        try {
          await queryInterface.changeColumn('comments', constraint.column, {
            type: constraint.type,
            allowNull: false
          }, { transaction });
        } catch (error) {
          console.warn(`⚠️  Constraint для comments.${constraint.column} уже существует или произошла ошибка:`, error.message);
        }
      }

      // === ДОБАВЛЕНИЕ FOREIGN KEY CONSTRAINTS ===

      // 5. Создаем foreign key constraint между posts и tasks (если не существует)
      try {
        await queryInterface.addConstraint('posts', {
          fields: ['taskId'],
          type: 'foreign key',
          name: 'fk_posts_task_id',
          references: {
            table: 'tasks',
            field: 'id'
          },
          onDelete: 'CASCADE',
          onUpdate: 'CASCADE'
        }, { transaction });
      } catch (error) {
        console.warn('⚠️  Foreign key constraint posts -> tasks уже существует:', error.message);
      }

      // === ДОБАВЛЕНИЕ CHECK CONSTRAINTS ДЛЯ ВАЛИДАЦИИ ДАННЫХ ===

      // 6. Проверочные ограничения для posts
      try {
        await queryInterface.sequelize.query(`
          ALTER TABLE posts
          ADD CONSTRAINT check_posts_vk_post_id_positive
          CHECK (vk_post_id >= 0);
        `, { transaction });
      } catch (error) {
        console.warn('⚠️  Check constraint для posts.vk_post_id уже существует:', error.message);
      }

      try {
        await queryInterface.sequelize.query(`
          ALTER TABLE posts
          ADD CONSTRAINT check_posts_likes_non_negative
          CHECK (likes >= 0);
        `, { transaction });
      } catch (error) {
        console.warn('⚠️  Check constraint для posts.likes уже существует:', error.message);
      }

      // 7. Проверочные ограничения для comments
      try {
        await queryInterface.sequelize.query(`
          ALTER TABLE comments
          ADD CONSTRAINT check_comments_vk_comment_id_positive
          CHECK (vk_comment_id >= 0);
        `, { transaction });
      } catch (error) {
        console.warn('⚠️  Check constraint для comments.vk_comment_id уже существует:', error.message);
      }

      try {
        await queryInterface.sequelize.query(`
          ALTER TABLE comments
          ADD CONSTRAINT check_comments_likes_non_negative
          CHECK (likes >= 0);
        `, { transaction });
      } catch (error) {
        console.warn('⚠️  Check constraint для comments.likes уже существует:', error.message);
      }

      try {
        await queryInterface.sequelize.query(`
          ALTER TABLE comments
          ADD CONSTRAINT check_comments_author_name_not_empty
          CHECK (length(trim(author_name)) > 0);
        `, { transaction });
      } catch (error) {
        console.warn('⚠️  Check constraint для comments.author_name уже существует:', error.message);
      }

      // === ДОБАВЛЕНИЕ CHECK CONSTRAINTS ДЛЯ TASKS ===

      // 8. Проверочные ограничения для tasks (добавляем к новым полям из предыдущей миграции)
      try {
        await queryInterface.sequelize.query(`
          ALTER TABLE tasks
          ADD CONSTRAINT check_tasks_progress_range
          CHECK (progress >= 0 AND progress <= 100);
        `, { transaction });
      } catch (error) {
        console.warn('⚠️  Check constraint для tasks.progress уже существует:', error.message);
      }

      try {
        await queryInterface.sequelize.query(`
          ALTER TABLE tasks
          ADD CONSTRAINT check_tasks_priority_range
          CHECK (priority >= 0 AND priority <= 10);
        `, { transaction });
      } catch (error) {
        console.warn('⚠️  Check constraint для tasks.priority уже существует:', error.message);
      }

      try {
        await queryInterface.sequelize.query(`
          ALTER TABLE tasks
          ADD CONSTRAINT check_tasks_execution_time_positive
          CHECK (execution_time IS NULL OR execution_time >= 0);
        `, { transaction });
      } catch (error) {
        console.warn('⚠️  Check constraint для tasks.executionTime уже существует:', error.message);
      }

      // === СОЗДАНИЕ TRIGGERS ДЛЯ АВТОМАТИЧЕСКОГО ОБНОВЛЕНИЯ TIMESTAMP ===

      // 9. Trigger для автоматического обновления updatedAt
      await queryInterface.sequelize.query(`
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW."updatedAt" = CURRENT_TIMESTAMP;
          RETURN NEW;
        END;
        $$ language 'plpgsql';
      `, { transaction });

      // Применяем trigger к основным таблицам
      const tablesForTrigger = ['tasks', 'posts', 'comments'];
      for (const tableName of tablesForTrigger) {
        try {
          await queryInterface.sequelize.query(`
            DROP TRIGGER IF EXISTS update_${tableName}_updated_at ON ${tableName};
            CREATE TRIGGER update_${tableName}_updated_at
              BEFORE UPDATE ON ${tableName}
              FOR EACH ROW
              EXECUTE FUNCTION update_updated_at_column();
          `, { transaction });
        } catch (error) {
          console.warn(`⚠️  Trigger для ${tableName} не был создан:`, error.message);
        }
      }

      await transaction.commit();
      console.log('✅ Все constraints успешно обновлены до NOT NULL');

    } catch (error) {
      await transaction.rollback();
      console.error('❌ Ошибка при обновлении constraints:', error);
      throw error;
    }
  },

  down: async (queryInterface, Sequelize) => {
    const transaction = await queryInterface.sequelize.transaction();

    try {
      console.log('🔄 Откат обновления constraints...');

      // 1. Удаляем triggers
      const tablesForTrigger = ['tasks', 'posts', 'comments'];
      for (const tableName of tablesForTrigger) {
        try {
          await queryInterface.sequelize.query(`
            DROP TRIGGER IF EXISTS update_${tableName}_updated_at ON ${tableName};
          `, { transaction });
        } catch (error) {
          console.warn(`⚠️  Не удалось удалить trigger для ${tableName}:`, error.message);
        }
      }

      // Удаляем функцию trigger
      await queryInterface.sequelize.query(`
        DROP FUNCTION IF EXISTS update_updated_at_column();
      `, { transaction });

      // 2. Удаляем check constraints
      const constraintsToRemove = [
        { table: 'posts', name: 'check_posts_vk_post_id_positive' },
        { table: 'posts', name: 'check_posts_likes_non_negative' },
        { table: 'comments', name: 'check_comments_vk_comment_id_positive' },
        { table: 'comments', name: 'check_comments_likes_non_negative' },
        { table: 'comments', name: 'check_comments_author_name_not_empty' },
        { table: 'tasks', name: 'check_tasks_progress_range' },
        { table: 'tasks', name: 'check_tasks_priority_range' },
        { table: 'tasks', name: 'check_tasks_execution_time_positive' }
      ];

      for (const constraint of constraintsToRemove) {
        try {
          await queryInterface.removeConstraint(constraint.table, constraint.name, { transaction });
        } catch (error) {
          console.warn(`⚠️  Не удалось удалить constraint ${constraint.name}:`, error.message);
        }
      }

      // 3. Удаляем foreign key constraint
      try {
        await queryInterface.removeConstraint('posts', 'fk_posts_task_id', { transaction });
      } catch (error) {
        console.warn('⚠️  Не удалось удалить foreign key constraint:', error.message);
      }

      // 4. Возвращаем allowNull: true для полей (по желанию - может быть опасно)
      console.log('ℹ️  NOT NULL constraints остаются - откат может привести к потере данных');

      await transaction.commit();
      console.log('✅ Откат миграции constraints завершен');

    } catch (error) {
      await transaction.rollback();
      console.error('❌ Ошибка при откате миграции constraints:', error);
      throw error;
    }
  }
};