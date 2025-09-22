package main

import (
	"fmt"
	"log"
	"net/http"
	"time"

	"backend/internal/domain/comments"
	"backend/internal/domain/keywords"
	"backend/internal/domain/settings"
	"backend/internal/domain/users"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
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

	// Prometheus middleware
	r.Use(promMiddleware)

	// Регистрация роутов
	setupRoutes(r)

	// Metrics endpoint
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))

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

// initDatabase инициализирует подключение к базе данных с GORM instrumentation
func initDatabase(dsn string) (*gorm.DB, error) {
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}

	// GORM tracing
	db.Callback().Create().Before("gorm:before_create").Register("trace:before_create", func(db *gorm.DB) {
		start := time.Now()
		db.InstanceSet("trace_start", start)
	})
	db.Callback().Create().After("gorm:after_create").Register("trace:after_create", func(db *gorm.DB) {
		if start, ok := db.InstanceGet("trace_start"); ok {
			duration := time.Since(start.(time.Time))
			// Note: Define GormCreateDuration in metrics.go
			// GormCreateDuration.WithLabelValues("model").Observe(duration.Seconds())
		}
	})

	db.Callback().Query().Before("gorm:before_query").Register("trace:before_query", func(db *gorm.DB) {
		start := time.Now()
		db.InstanceSet("trace_start", start)
	})
	db.Callback().Query().After("gorm:after_query").Register("trace:after_query", func(db *gorm.DB) {
		if start, ok := db.InstanceGet("trace_start"); ok {
			duration := time.Since(start.(time.Time))
			// Note: Define GormQueryDuration in metrics.go
			// GormQueryDuration.WithLabelValues("model").Observe(duration.Seconds())
		}
	})

	// Connection pool monitoring
	go func() {
		for {
			stats := sqlDB.Stats()
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
