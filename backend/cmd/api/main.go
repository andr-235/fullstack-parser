// Package main содержит точку входа в приложение.
package main

import (
	"log"
	"time"

	authHandlers "backend/internal/delivery/http/handlers/auth"
	settingsHandlers "backend/internal/delivery/http/handlers/settings"
	usersHandlers "backend/internal/delivery/http/handlers/users"
	"backend/internal/delivery/http/middleware"
	"backend/internal/domain/settings"
	"backend/internal/domain/users"
	postgresRepo "backend/internal/repository/postgres"
	settingsUsecase "backend/internal/usecase/settings"
	usersUsecase "backend/internal/usecase/users"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"github.com/spf13/viper"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// Config содержит конфигурацию приложения
type Config struct {
	JWTSecret  string
	DSN        string
	AccessTTL  time.Duration
	RefreshTTL time.Duration
}

// loadConfig загружает конфигурацию из файла
func loadConfig() *Config {
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")

	if err := viper.ReadInConfig(); err != nil {
		log.Fatal("Ошибка чтения конфига:", err)
	}

	return &Config{
		JWTSecret:  viper.GetString("jwt.secret"),
		DSN:        viper.GetString("database.dsn"),
		AccessTTL:  15 * time.Minute,
		RefreshTTL: 168 * time.Hour,
	}
}

// initDatabase инициализирует подключение к БД и выполняет миграции
func initDatabase(dsn string) *gorm.DB {
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal("Ошибка подключения к БД:", err)
	}

	// Автомиграция
	if err := db.AutoMigrate(&users.User{}, &settings.Setting{}); err != nil {
		log.Fatal("Ошибка миграции БД:", err)
	}

	return db
}

// setupHandlers инициализирует все handlers и use cases
func setupHandlers(db *gorm.DB, config *Config) (*authHandlers.AuthHandler, *usersHandlers.UserHandler, *settingsHandlers.SettingsHandler) {
	// Репозитории
	userRepo := postgresRepo.NewUserRepository(db)
	settingRepo := postgresRepo.NewSettingPostgresRepository(db)

	// Use cases
	userUseCase := usersUsecase.NewUserUseCase(userRepo)
	authUseCase := usersUsecase.NewAuthUseCase(userRepo, config.JWTSecret, config.AccessTTL, config.RefreshTTL)
	settingsUsecase := settingsUsecase.NewSettingsUsecase(settingRepo, userRepo, logrus.New())

	// Handlers
	authHandler := authHandlers.NewAuthHandler(authUseCase, userUseCase)
	userHandler := usersHandlers.NewUserHandler(userUseCase)
	settingsHandler := settingsHandlers.NewSettingsHandler(settingsUsecase, logrus.New())

	return authHandler, userHandler, settingsHandler
}

// setupRoutes настраивает маршруты API
func setupRoutes(authHandler *authHandlers.AuthHandler, userHandler *usersHandlers.UserHandler, settingsHandler *settingsHandlers.SettingsHandler, jwtSecret string) *gin.Engine {
	r := gin.Default()

	api := r.Group("/api/v1")
	{
		// Аутентификация (публичные маршруты)
		authGroup := api.Group("/auth")
		{
			authGroup.POST("/register", authHandler.Register)
			authGroup.POST("/login", authHandler.Login)
			authGroup.POST("/refresh", authHandler.Refresh)
		}

		// Пользователи (требуют аутентификации)
		usersGroup := api.Group("/users")
		usersGroup.Use(middleware.JWTAuth(jwtSecret))
		{
			usersGroup.GET("/:id", userHandler.GetUser)
			usersGroup.PUT("/:id", userHandler.UpdateUser)
			usersGroup.DELETE("/:id", userHandler.DeleteUser)
			usersGroup.GET("/", middleware.AdminOnly(), userHandler.ListUsers)
		}

		// Настройки (требуют аутентификации и права администратора)
		settingsGroup := api.Group("/settings")
		settingsGroup.Use(middleware.JWTAuth(jwtSecret))
		settingsGroup.Use(middleware.AdminOnly())
		{
			settingsGroup.GET("/", settingsHandler.GetSettings)
			settingsGroup.GET("/:key", settingsHandler.GetSettingByKey)
			settingsGroup.POST("/", settingsHandler.CreateSetting)
			settingsGroup.PUT("/:key", settingsHandler.UpdateSetting)
			settingsGroup.DELETE("/:key", settingsHandler.DeleteSetting)
		}
	}

	return r
}

func main() {
	// Загрузка конфигурации
	config := loadConfig()

	// Инициализация БД
	db := initDatabase(config.DSN)
	defer func() {
		if sqlDB, err := db.DB(); err == nil {
			sqlDB.Close()
		}
	}()

	// Настройка handlers
	authHandler, userHandler, settingsHandler := setupHandlers(db, config)

	// Настройка маршрутов
	router := setupRoutes(authHandler, userHandler, settingsHandler, config.JWTSecret)

	// Запуск сервера
	if err := router.Run(":8080"); err != nil {
		log.Fatal("Ошибка запуска сервера:", err)
	}
}
