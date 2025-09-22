package main

import (
	"log"
	"time"

	"backend/internal/domain/comments"
	"backend/internal/domain/keywords"
	"backend/internal/domain/settings"
	"backend/internal/domain/users"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// Config содержит конфигурацию приложения
type Config struct {
	DatabaseDSN string
	JWTSecret   string
	AccessTTL   time.Duration
	RefreshTTL  time.Duration
	Port        string
}

func main() {
	logger := logrus.New()
	logger.SetLevel(logrus.InfoLevel)

	// Конфигурация приложения
	config := getConfig()

	// Инициализация базы данных
	db, err := initDatabase(config.DatabaseDSN)
	if err != nil {
		log.Fatal("failed to connect database:", err)
	}

	// Миграции
	if err := runMigrations(db); err != nil {
		log.Fatal("failed to run migrations:", err)
	}

	// Инициализация зависимостей
	initDependencies(db, config, logger)

	// HTTP роутер
	r := gin.Default()

	// Регистрация роутов
	setupRoutes(r)

	// Запуск сервера
	logger.Infof("Starting server on port %s", config.Port)
	if err := r.Run(":" + config.Port); err != nil {
		log.Fatal("failed to start server:", err)
	}
}

// getConfig возвращает конфигурацию приложения
func getConfig() *Config {
	return &Config{
		DatabaseDSN: "host=localhost user=postgres password=postgres dbname=vk_comments port=5432 sslmode=disable TimeZone=UTC",
		JWTSecret:   "your-jwt-secret-key-change-in-production",
		AccessTTL:   15 * time.Minute,
		RefreshTTL:  24 * time.Hour,
		Port:        "8080",
	}
}

// initDatabase инициализирует подключение к базе данных
func initDatabase(dsn string) (*gorm.DB, error) {
	return gorm.Open(postgres.Open(dsn), &gorm.Config{})
}

// runMigrations выполняет миграции базы данных
func runMigrations(db *gorm.DB) error {
	return db.AutoMigrate(
		&users.User{},
		&comments.Comment{},
		&settings.Setting{},
		&keywords.Keyword{},
	)
}

// initDependencies инициализирует все зависимости приложения
func initDependencies(db *gorm.DB, config *Config, logger *logrus.Logger) {
	// Здесь будет инициализация зависимостей
	// Пока что просто логируем
	logger.Info("Dependencies initialized")
}

// setupRoutes настраивает все роуты приложения
func setupRoutes(r *gin.Engine) {
	// API v1 группа
	v1 := r.Group("/api/v1")

	// Базовый роут для проверки работоспособности
	v1.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "ok",
			"message": "Server is running",
		})
	})

	// Заглушки для будущих роутов
	auth := v1.Group("/auth")
	{
		auth.GET("/", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "Auth endpoints coming soon"})
		})
	}

	users := v1.Group("/users")
	{
		users.GET("/", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "Users endpoints coming soon"})
		})
	}

	comments := v1.Group("/comments")
	{
		comments.GET("/", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "Comments endpoints coming soon"})
		})
	}

	keywords := v1.Group("/keywords")
	{
		keywords.GET("/", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "Keywords endpoints coming soon"})
		})
	}

	settings := v1.Group("/settings")
	{
		settings.GET("/", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "Settings endpoints coming soon"})
		})
	}
}
