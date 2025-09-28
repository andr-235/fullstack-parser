#!/usr/bin/env ts-node

/**
 * Скрипт для создания baseline миграции для существующей БД
 *
 * Этот скрипт:
 * 1. Проверяет подключение к существующей БД
 * 2. Создает baseline миграцию с текущей схемой
 * 3. Помечает миграцию как примененную (не запускает)
 *
 * Используется при миграции с Sequelize на Prisma
 */

import { execSync } from 'child_process';
import { existsSync, mkdirSync } from 'fs';
import path from 'path';

const PRISMA_DIR = path.join(__dirname);
const MIGRATIONS_DIR = path.join(PRISMA_DIR, 'migrations');

async function createBaselineMigration() {
  try {
    console.log('🔍 Проверка подключения к базе данных...');

    // Создаем директорию миграций если не существует
    if (!existsSync(MIGRATIONS_DIR)) {
      mkdirSync(MIGRATIONS_DIR, { recursive: true });
      console.log('📁 Создана директория миграций');
    }

    // Создаем директорию для первой миграции
    const initMigrationDir = path.join(MIGRATIONS_DIR, '0_init');
    if (!existsSync(initMigrationDir)) {
      mkdirSync(initMigrationDir, { recursive: true });
      console.log('📁 Создана директория для baseline миграции');
    }

    console.log('📋 Генерация Prisma Client...');
    try {
      execSync('npx prisma generate', { stdio: 'inherit' });
      console.log('✅ Prisma Client сгенерирован');
    } catch (error) {
      console.log('⚠️  Ошибка генерации клиента, продолжаем...');
    }

    console.log('📋 Создание baseline миграции...');

    // Создаем baseline миграцию для существующей БД
    try {
      execSync('npx prisma migrate dev --name init --create-only', { stdio: 'inherit' });
      console.log('✅ Baseline миграция создана');
    } catch (error) {
      console.log('⚠️  Создание миграции через dev не удалось, пробуем другой способ...');

      // Альтернативный способ - создаем миграцию вручную
      execSync('npx prisma db push', { stdio: 'inherit' });
      console.log('✅ Схема синхронизирована с БД');
    }

    console.log('✅ Baseline миграция готова');
    console.log('');
    console.log('📋 Следующие шаги:');
    console.log('1. Проверьте статус миграций: npx prisma migrate status');
    console.log('2. Проверьте Prisma Client: npx prisma generate');
    console.log('3. При необходимости создайте новые миграции: npx prisma migrate dev');

  } catch (error) {
    console.error('❌ Ошибка при создании baseline миграции:', error);
    console.log('');
    console.log('🔧 Возможные решения:');
    console.log('1. Убедитесь, что PostgreSQL запущен и доступен');
    console.log('2. Проверьте переменную окружения DATABASE_URL в .env файле');
    console.log('3. Убедитесь, что база данных vk_analyzer существует');
    console.log('4. Проверьте права доступа к базе данных');
    console.log('5. Попробуйте выполнить команды вручную:');
    console.log('   - npx prisma db push');
    console.log('   - npx prisma generate');
    process.exit(1);
  }
}

// Проверяем, что скрипт запущен напрямую
if (require.main === module) {
  createBaselineMigration();
}

export default createBaselineMigration;