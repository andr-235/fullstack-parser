import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// IIFE для асинхронной инициализации приложения
(async () => {
  console.log("DEBUG: Начало асинхронной инициализации приложения");

  try {
    // Импорт и инициализация модуля аутентификации
    console.log("DEBUG: Импорт auth модуля...");
    const { initializeAuth, startTokenMiddleware } = await import('./auth');
    console.log("DEBUG: Auth модуль импортирован успешно");

    const app = createApp(App);

    app.use(createPinia());
    app.use(router);

    // Инициализация системы аутентификации
    console.log("DEBUG: Вызов initializeAuth()");
    await initializeAuth();
    console.log("DEBUG: initializeAuth() завершён успешно");

    app.mount('#app');

    // Запуск middleware токенов после монтирования приложения
    console.log("DEBUG: Вызов startTokenMiddleware()");
    await startTokenMiddleware();
    console.log("DEBUG: startTokenMiddleware() завершён успешно");

    console.log("DEBUG: Асинхронная инициализация приложения завершена");
  } catch (error) {
    console.error("DEBUG: Ошибка при инициализации приложения:", error);
    console.error("DEBUG: Stack trace:", error instanceof Error ? error.stack : 'No stack trace');
    throw error;
  }
})();