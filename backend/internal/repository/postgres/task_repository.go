package postgres

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"backend/internal/domain/tasks"
	"backend/internal/repository"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// TaskRepository реализует интерфейс TaskRepository для PostgreSQL.
type TaskRepository struct {
	db *gorm.DB
}

// NewTaskRepository создает новый репозиторий задач.
func NewTaskRepository(db *gorm.DB) *TaskRepository {
	return &TaskRepository{db: db}
}

// TaskModel представляет модель задачи в базе данных.
type TaskModel struct {
	ID        string    `gorm:"primaryKey;type:varchar(36)"`
	Type      string    `gorm:"type:varchar(50);not null"`
	Payload   string    `gorm:"type:jsonb;not null"`
	Status    string    `gorm:"type:varchar(20);not null;default:'pending'"`
	Result    string    `gorm:"type:jsonb"`
	Error     string    `gorm:"type:text"`
	CreatedAt time.Time `gorm:"not null"`
	UpdatedAt time.Time
}

// TableName возвращает имя таблицы для модели.
func (TaskModel) TableName() string {
	return "tasks"
}

// Enqueue добавляет задачу в очередь.
func (r *TaskRepository) Enqueue(ctx context.Context, req *tasks.EnqueueRequest) (string, error) {
	taskID := uuid.New().String()

	payloadJSON, err := json.Marshal(req.Payload)
	if err != nil {
		return "", fmt.Errorf("marshal payload: %w", err)
	}

	task := TaskModel{
		ID:        taskID,
		Type:      req.Type,
		Payload:   string(payloadJSON),
		Status:    string(tasks.StatusPending),
		CreatedAt: time.Now(),
	}

	if err := r.db.WithContext(ctx).Create(&task).Error; err != nil {
		return "", fmt.Errorf("create task: %w", err)
	}

	return taskID, nil
}

// GetTask получает задачу по ID.
func (r *TaskRepository) GetTask(ctx context.Context, id string) (*tasks.TaskResponse, error) {
	var task TaskModel

	if err := r.db.WithContext(ctx).Where("id = ?", id).First(&task).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, repository.ErrNotFound
		}
		return nil, fmt.Errorf("get task: %w", err)
	}

	var result json.RawMessage
	if task.Result != "" {
		result = json.RawMessage(task.Result)
	}

	return &tasks.TaskResponse{
		ID:     task.ID,
		Status: tasks.Status(task.Status),
		Result: result,
		Error:  task.Error,
	}, nil
}

// CancelTask отменяет задачу.
func (r *TaskRepository) CancelTask(ctx context.Context, id string) error {
	result := r.db.WithContext(ctx).Model(&TaskModel{}).
		Where("id = ? AND status IN ?", id, []string{string(tasks.StatusPending), string(tasks.StatusActive)}).
		Updates(map[string]interface{}{
			"status":     string(tasks.StatusCanceled),
			"updated_at": time.Now(),
		})

	if result.Error != nil {
		return fmt.Errorf("cancel task: %w", result.Error)
	}

	if result.RowsAffected == 0 {
		return repository.ErrNotFound
	}

	return nil
}

// ListTasks возвращает список задач с фильтрацией.
func (r *TaskRepository) ListTasks(ctx context.Context, req *tasks.ListRequest) (*tasks.ListResponse, error) {
	var tasksModels []TaskModel
	var total int64

	query := r.db.WithContext(ctx).Model(&TaskModel{})

	// Применяем фильтры
	if req.Type != nil {
		query = query.Where("type = ?", *req.Type)
	}
	if req.Status != nil {
		query = query.Where("status = ?", *req.Status)
	}

	// Подсчитываем общее количество
	if err := query.Count(&total).Error; err != nil {
		return nil, fmt.Errorf("count tasks: %w", err)
	}

	// Применяем пагинацию
	offset := (req.Page - 1) * req.Limit
	if err := query.Order("created_at DESC").
		Offset(offset).
		Limit(req.Limit).
		Find(&tasksModels).Error; err != nil {
		return nil, fmt.Errorf("list tasks: %w", err)
	}

	// Преобразуем в ответ
	taskResponses := make([]tasks.TaskResponse, len(tasksModels))
	for i, task := range tasksModels {
		var result json.RawMessage
		if task.Result != "" {
			result = json.RawMessage(task.Result)
		}

		taskResponses[i] = tasks.TaskResponse{
			ID:     task.ID,
			Status: tasks.Status(task.Status),
			Result: result,
			Error:  task.Error,
		}
	}

	return &tasks.ListResponse{
		Tasks: taskResponses,
		Total: total,
		Page:  req.Page,
		Limit: req.Limit,
	}, nil
}

// GetStats возвращает статистику задач.
func (r *TaskRepository) GetStats(ctx context.Context) (*tasks.StatsResponse, error) {
	var stats tasks.StatsResponse

	// Подсчитываем задачи по статусам
	statusCounts := make(map[string]int64)

	rows, err := r.db.WithContext(ctx).Model(&TaskModel{}).
		Select("status, COUNT(*) as count").
		Group("status").
		Rows()
	if err != nil {
		return nil, fmt.Errorf("get stats: %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		var status string
		var count int64
		if err := rows.Scan(&status, &count); err != nil {
			return nil, fmt.Errorf("scan stats: %w", err)
		}
		statusCounts[status] = count
	}

	stats.Pending = int(statusCounts[string(tasks.StatusPending)])
	stats.Active = int(statusCounts[string(tasks.StatusActive)])
	stats.Completed = int(statusCounts[string(tasks.StatusCompleted)])
	stats.Failed = int(statusCounts[string(tasks.StatusFailed)])
	stats.Canceled = int(statusCounts[string(tasks.StatusCanceled)])

	return &stats, nil
}

// UpdateTaskStatus обновляет статус задачи.
func (r *TaskRepository) UpdateTaskStatus(ctx context.Context, id string, status tasks.Status, result json.RawMessage, errorMsg string) error {
	updates := map[string]interface{}{
		"status":     string(status),
		"updated_at": time.Now(),
	}

	if result != nil {
		resultJSON, err := json.Marshal(result)
		if err != nil {
			return fmt.Errorf("marshal result: %w", err)
		}
		updates["result"] = string(resultJSON)
	}

	if errorMsg != "" {
		updates["error"] = errorMsg
	}

	if err := r.db.WithContext(ctx).Model(&TaskModel{}).
		Where("id = ?", id).
		Updates(updates).Error; err != nil {
		return fmt.Errorf("update task status: %w", err)
	}

	return nil
}
