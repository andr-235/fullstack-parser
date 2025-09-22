package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"backend/internal/config"
	"backend/internal/domain/comments"
	"backend/internal/domain/keywords"
	"backend/internal/domain/settings"
	"backend/internal/domain/users"
	"backend/internal/logger"

	"github.com/gin-gonic/gin"
	"github.com/gin-contrib/cors"
	"github.com/google/uuid"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/sirupsen/logrus"
	"github.com/swaggo/files"
	"github.com/swaggo/gin-swagger"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// @title VK Parser API
// @version 1.0
// @description API для парсинга VK с морфологическим анализом ключевых слов
// @host localhost:8080
// @BasePath /api/v1
// @schemes http

func main() {
	logger := logrus.New()
	logger.SetLevel(logrus.InfoLevel)

	// Конфигурация приложения
	cfg, err := config.LoadConfig("config/config.yaml")
	if err != nil {
		log.Fatal("failed to load config:", err)
	}
	logger.SetLevel(logrus.ParseLevel(cfg.Log.Level))

	// Инициализация базы данных
	db, err := initDatabase(cfg.Database.URL)
	if err != nil {
		log.Fatal("failed to connect database:", err)
	}

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
	initDependencies(db, cfg, logger)

	// HTTP metrics
	var (
		httpRequestsTotal = promauto.NewCounterVec(
			prometheus.CounterOpts{
				Name: "http_requests_total",
				Help: "Total number of HTTP requests",
			},
			[]string{"method", "path", "status"},
		)

		httpRequestDuration = promauto.NewHistogramVec(
			prometheus.HistogramOpts{
				Name: "http_request_duration_seconds",
				Help: "Duration of HTTP requests in seconds",
			},
			[]string{"method", "path"},
		)
	)

	// Custom Prometheus middleware for Gin
	promMiddleware := func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		method := c.Request.Method

		c.Next()

		status := fmt.Sprintf("%d", c.Writer.Status())
		duration := time.Since(start).Seconds()

		httpRequestsTotal.WithLabelValues(method, path, status).Inc()
		httpRequestDuration.WithLabelValues(method, path).Observe(duration)
	}

	// HTTP роутер
	r := gin.Default()

	// CORS middleware
	r.Use(cors.Default())

	// Correlation ID middleware
	correlationMiddleware := func(c *gin.Context) {
		id := uuid.New().String()
		c.Set("correlation_id", id)
		c.Header("X-Correlation-ID", id)
		c.Next()
	}

	// Prometheus middleware
	r.Use(correlationMiddleware)
	r.Use(promMiddleware)

	// Регистрация роутов
	setupRoutes(r)

	// Swagger docs
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// Metrics endpoint
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))

	// Graceful shutdown
	srv := &http.Server{
		Addr:    ":" + cfg.Server.Port,
		Handler: r,
	}

	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %s\n", err)
		}
	}()

	logger.Infof("Starting server on port %s", cfg.Server.Port)

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	logger.Info("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}

	logger.Info("Server exiting")
}

// getConfig возвращает конфигурацию приложения
func getConfig() *Config {
	// Получаем переменные окружения или используем значения по умолчанию
	databaseDSN := os.Getenv("DATABASE_DSN")
	if databaseDSN == "" {
		databaseDSN = "host=postgres user=postgres password=postgres dbname=vk_parser port=5432 sslmode=disable TimeZone=UTC"
	}

	jwtSecret := os.Getenv("JWT_SECRET")
	if jwtSecret == "" {
		jwtSecret = "your-jwt-secret-key-change-in-production"
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	return &Config{
		DatabaseDSN: databaseDSN,
		JWTSecret:   jwtSecret,
		AccessTTL:   15 * time.Minute,
		RefreshTTL:  24 * time.Hour,
		RedisAddr:   "redis:6379",
		Port:        port,
	}
}

// initDatabase инициализирует подключение к базе данных с GORM instrumentation
func initDatabase(dsn string) (*gorm.DB, error) {
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.NewPrometheusLogger(),
	})
	if err != nil {
		return nil, err
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}

	// Connection pool monitoring
	go func() {
		for {
			stats := sqlDB.Stats()
			_ = stats // Suppress unused variable warning
			// Note: Define GormDBOpenConnections in metrics.go
			// GormDBOpenConnections.WithLabelValues("db").Set(float64(stats.OpenConnections))
			// GormDBInUse.WithLabelValues("db").Set(float64(stats.InUse))
			// GormDBIdle.WithLabelValues("db").Set(float64(stats.Idle))
			time.Sleep(10 * time.Second)
		}
	}()

	return db, nil
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
