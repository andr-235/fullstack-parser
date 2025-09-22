package tasks

import (
	"encoding/json"
	"time"
)

// Task представляет сущность задачи в системе очередей.
type Task struct {
	ID        string          `json:"id" gorm:"primaryKey;type:varchar(36)"`
	Type      string          `json:"type" gorm:"type:varchar(50);not null;index"`      // Тип задачи, например "analyze_comment"
	Payload   json.RawMessage `json:"payload" gorm:"type:jsonb;not null"`   // Полезная нагрузка задачи в JSON
	Status    Status          `json:"status" gorm:"type:varchar(20);not null;default:'pending';index"`    // Статус задачи
	Result    json.RawMessage `json:"result" gorm:"type:jsonb"`    // Результат выполнения (JSON)
	Error     string          `json:"error,omitempty" gorm:"type:text"` // Ошибка, если статус failed
	CreatedAt time.Time       `json:"created_at" gorm:"not null"`
	UpdatedAt time.Time       `json:"updated_at,omitempty"`
}

// Status - статус задачи.
type Status string

const (
	StatusPending   Status = "pending"   // Задача ожидает выполнения
	StatusActive    Status = "active"    // Задача выполняется
	StatusCompleted Status = "completed" // Задача успешно завершена
	StatusFailed    Status = "failed"    // Задача завершилась с ошибкой
	StatusCanceled  Status = "canceled"  // Задача отменена
)

// EnqueueRequest - запрос на постановку задачи в очередь.
type EnqueueRequest struct {
	Type    string          `json:"type" binding:"required"`
	Payload json.RawMessage `json:"payload" binding:"required"`
}

// TaskResponse - ответ с информацией о задаче.
type TaskResponse struct {
	ID     string          `json:"id"`
	Status Status          `json:"status"`
	Result json.RawMessage `json:"result,omitempty"`
	Error  string          `json:"error,omitempty"`
}

// ListRequest - параметры для списка задач.
type ListRequest struct {
	Type   *string `json:"type,omitempty" form:"type"`
	Status *string `json:"status,omitempty" form:"status"`
	Page   int     `json:"page" form:"page" binding:"min=1"`
	Limit  int     `json:"limit" form:"limit" binding:"min=1,max=100"`
}

// ListResponse - ответ со списком задач.
type ListResponse struct {
	Tasks   []TaskResponse `json:"tasks"`
	Total   int64          `json:"total"`
	Page    int            `json:"page"`
	Limit   int            `json:"limit"`
}

// StatsResponse - статистика очередей.
type StatsResponse struct {
	Pending   int `json:"pending"`
	Active    int `json:"active"`
	Completed int `json:"completed"`
	Failed    int `json:"failed"`
	Canceled  int `json:"canceled"`
}