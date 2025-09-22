package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"backend/internal/usecase/tasks"

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
	return &Config{
		DatabaseDSN: "host=localhost user=postgres password=postgres dbname=vk_comments port=5432 sslmode=disable TimeZone=UTC",
		RedisAddr:   "localhost:6379",
		RedisPass:   "",
	}
}

// initDatabase инициализирует подключение к базе данных
func initDatabase(dsn string) (*gorm.DB, error) {
	return gorm.Open(postgres.Open(dsn), &gorm.Config{})
}

// parseCommentsTask обрабатывает задачу парсинга комментариев
func parseCommentsTask(ctx context.Context, t *asynq.Task) error {
	// Извлечение payload
	var payload struct {
		TaskID string `json:"task_id"`
		GroupID int64 `json:"group_id"`
		PostID int64 `json:"post_id"`
	}
	if err := json.Unmarshal(t.Payload(), &payload); err != nil {
		return fmt.Errorf("json.Unmarshal failed: %v", err)
	}

	// Инициализация usecase
	db, err := initDatabase(getConfig().DatabaseDSN)
	if err != nil {
		return fmt.Errorf("database init failed: %v", err)
	}
	defer db.Close()

	taskUsecase := tasks.NewTasksUsecase(db) // Адаптировать под реальный constructor из tasks_usecase.go

	// Выполнение задачи
	if err := taskUsecase.ProcessComments(payload.GroupID, payload.PostID); err != nil {
		return fmt.Errorf("process comments failed: %v", err)
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
	defer db.Close()

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
	mux.HandleFunc("comments:parse", parseCommentsTask) // Пример handler для задачи парсинга комментариев

	if err := srv.Run(mux); err != nil {
		log.Fatal("Worker run failed:", err)
	}
}