package main

import (
	"backend/internal/usecase/tasks"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/hibiken/asynq"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// Config содержит конфигурацию worker
type Config struct {
	DatabaseDSN string
	RedisAddr   string
	RedisPass   string
}

// getConfig возвращает конфигурацию worker
func getConfig() *Config {
	databaseDSN := os.Getenv("DATABASE_DSN")
	if databaseDSN == "" {
		databaseDSN = "host=postgres user=postgres password=postgres dbname=vk_parser port=5432 sslmode=disable TimeZone=UTC"
	}

	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		redisAddr = "redis:6379"
	}

	redisPass := os.Getenv("REDIS_PASS")

	return &Config{
		DatabaseDSN: databaseDSN,
		RedisAddr:   redisAddr,
		RedisPass:   redisPass,
	}
}

// initDatabase инициализирует подключение к базе данных
func initDatabase(dsn string) (*gorm.DB, error) {
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	// Получаем sql.DB для правильного закрытия
	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}

	// Настраиваем пул соединений
	sqlDB.SetMaxOpenConns(10)
	sqlDB.SetMaxIdleConns(5)

	return db, nil
}

// parseCommentsTask обрабатывает задачу парсинга комментариев
func parseCommentsTask(ctx context.Context, t *asynq.Task) error {
	// Извлечение payload
	var payload struct {
		TaskID  string `json:"task_id"`
		GroupID int64  `json:"group_id"`
		PostID  int64  `json:"post_id"`
	}
	if err := json.Unmarshal(t.Payload(), &payload); err != nil {
		return fmt.Errorf("json.Unmarshal failed: %v", err)
	}

	// Инициализация базы данных
	db, err := initDatabase(getConfig().DatabaseDSN)
	if err != nil {
		return fmt.Errorf("database init failed: %v", err)
	}
	defer func() {
		if sqlDB, err := db.DB(); err == nil {
			sqlDB.Close()
		}
	}()

	// Создаем usecase для обработки задач
	taskProcessor := tasks.NewTaskProcessorUsecase(db)

	// Обрабатываем задачу
	if err := taskProcessor.ProcessCommentsTask(ctx, payload.TaskID, payload.GroupID, payload.PostID); err != nil {
		return fmt.Errorf("process comments failed: %v", err)
	}

	return nil
}

// processTask универсальный обработчик задач
func processTask(ctx context.Context, t *asynq.Task) error {
	// Извлечение payload
	var payload struct {
		TaskID   string          `json:"task_id"`
		TaskType string          `json:"task_type"`
		Payload  json.RawMessage `json:"payload"`
	}
	if err := json.Unmarshal(t.Payload(), &payload); err != nil {
		return fmt.Errorf("json.Unmarshal failed: %v", err)
	}

	// Инициализация базы данных
	db, err := initDatabase(getConfig().DatabaseDSN)
	if err != nil {
		return fmt.Errorf("database init failed: %v", err)
	}
	defer func() {
		if sqlDB, err := db.DB(); err == nil {
			sqlDB.Close()
		}
	}()

	// Создаем usecase для обработки задач
	taskProcessor := tasks.NewTaskProcessorUsecase(db)

	// Обрабатываем задачу по типу
	if err := taskProcessor.ProcessTask(ctx, payload.TaskID, payload.TaskType, payload.Payload); err != nil {
		return fmt.Errorf("process task failed: %v", err)
	}

	return nil
}

func main() {
	config := getConfig()

	// Инициализация базы данных
	db, err := initDatabase(config.DatabaseDSN)
	if err != nil {
		log.Fatal("Database init failed:", err)
	}
	defer func() {
		if sqlDB, err := db.DB(); err == nil {
			sqlDB.Close()
		}
	}()

	// Настройка сервера worker
	srv := asynq.NewServer(
		asynq.RedisClientOpt{
			Addr:     config.RedisAddr,
			Password: config.RedisPass,
		},
		asynq.Config{
			Concurrency: 10,
		},
	)

	mux := asynq.NewServeMux()
	mux.HandleFunc("comments:parse", parseCommentsTask) // Handler для задачи парсинга комментариев
	mux.HandleFunc("task:process", processTask)         // Универсальный handler для обработки задач

	if err := srv.Run(mux); err != nil {
		log.Fatal("Worker run failed:", err)
	}
}
