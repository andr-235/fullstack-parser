# Backend

Серверная часть приложения для анализа VK комментариев на Node.js с TypeScript.

## Установка зависимостей

```bash
npm install
```

## Запуск

### Режим разработки (с автоперезагрузкой)
```bash
npm run dev:watch
```

### Режим разработки
```bash
npm run dev
```

### Сборка TypeScript в JavaScript
```bash
npm run build
```

### Запуск production версии
```bash
npm run start
```

## Тестирование

```bash
npm test
npm run test:watch
```

## Работа с базой данных (Prisma)

### Миграции
```bash
npm run prisma:migrate      # Применить миграции в dev режиме
npm run prisma:migrate:prod # Применить миграции в production
```

### Другие команды Prisma
```bash
npm run prisma:generate     # Генерация Prisma клиента
npm run prisma:studio       # Открыть Prisma Studio
npm run prisma:reset        # Сброс базы данных (ОСТОРОЖНО!)
```

Этот проект использует Node.js с TypeScript для серверной разработки и Express.js в качестве веб-фреймворка.
