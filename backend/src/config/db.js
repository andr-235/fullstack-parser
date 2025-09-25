const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(process.env.DB_URL, {
  // Включаем логирование SQL запросов в development режиме
  logging: process.env.NODE_ENV === 'development' ? console.log : false,

  // Connection pool конфигурация для оптимальной производительности
  pool: {
    max: 20,          // Максимальное количество соединений в пуле
    min: 0,           // Минимальное количество соединений в пуле
    acquire: 60000,   // Максимальное время в миллисекундах, которое пул будет пытаться получить соединение
    idle: 10000,      // Максимальное время в миллисекундах, которое соединение может быть неактивным
    evict: 1000,      // Интервал проверки соединений на предмет удаления из пула
    handleDisconnects: true  // Автоматическое переподключение при разрыве соединения
  },

  // Connection timeout настройки
  dialectOptions: {
    connectTimeout: 30000,    // Таймаут подключения (30 секунд)
    acquireConnectionTimeout: 60000,  // Таймаут получения соединения (60 секунд)
    timeout: 60000,           // Таймаут выполнения запроса (60 секунд)

    // SSL конфигурация для production
    ...(process.env.NODE_ENV === 'production' && {
      ssl: {
        require: true,
        rejectUnauthorized: false
      }
    })
  },

  // Дополнительные настройки производительности
  define: {
    // Автоматически добавляем timestamps ко всем моделям
    timestamps: true,
    // Используем camelCase для полей
    underscored: false,
    // Имена таблиц во множественном числе
    freezeTableName: false
  },

  // Query опции по умолчанию
  query: {
    // Используем prepared statements для лучшей производительности
    useMaster: true
  },

  // Benchmark для мониторинга производительности в development
  benchmark: process.env.NODE_ENV === 'development',

  // Настройки для различных диалектов PostgreSQL
  dialectModule: require('pg')
});

module.exports = sequelize;