const fs = require('fs').promises;
const path = require('path');
const { Pool } = require('pg');
const logger = require('../src/utils/logger.js');

async function runMigration() {
  // Используем localhost для локального запуска миграции
  const dbUrl = process.env.DB_URL?.replace('postgres:', 'localhost:') || 'postgresql://postgres:postgres@localhost:5432/vk_analyzer';
  
  const pool = new Pool({
    connectionString: dbUrl
  });
  
  try {
    // Читаем файл миграции
    const migrationPath = path.join(__dirname, '../migrations/001_create_groups_table.sql');
    const migrationSQL = await fs.readFile(migrationPath, 'utf-8');
    
    // Выполняем миграцию
    await pool.query(migrationSQL);
    
    logger.info('Migration completed successfully');
    console.log('✅ Migration completed successfully');
  } catch (error) {
    logger.error('Migration failed', { error: error.message });
    console.error('❌ Migration failed:', error.message);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

// Запускаем миграцию если файл выполняется напрямую
if (require.main === module) {
  runMigration();
}

module.exports = runMigration;
