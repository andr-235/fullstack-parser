package tasks

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"backend/internal/domain/tasks"
	"backend/internal/repository/postgres"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

// TaskProcessorUsecase - use case для обработки задач воркера.
type TaskProcessorUsecase struct {
	taskRepo *postgres.TaskRepository
	db       *gorm.DB
}

// NewTaskProcessorUsecase создает новый use case для обработки задач.
func NewTaskProcessorUsecase(db *gorm.DB) *TaskProcessorUsecase {
	return &TaskProcessorUsecase{
		taskRepo: postgres.NewTaskRepository(db),
		db:       db,
	}
}

// ProcessCommentsTask обрабатывает задачу парсинга комментариев.
func (u *TaskProcessorUsecase) ProcessCommentsTask(ctx context.Context, taskID string, groupID, postID int64) error {
	log := logrus.WithFields(logrus.Fields{
		"task_id":  taskID,
		"group_id": groupID,
		"post_id":  postID,
	})

	// Обновляем статус задачи на "выполняется"
	if err := u.taskRepo.UpdateTaskStatus(ctx, taskID, tasks.StatusActive, nil, ""); err != nil {
		log.WithError(err).Error("Failed to update task status to active")
		return fmt.Errorf("update task status: %w", err)
	}

	log.Info("Starting comment processing task")

	// Здесь будет реальная логика обработки комментариев
	// Пока что имитируем обработку
	result, err := u.processComments(groupID, postID)
	if err != nil {
		log.WithError(err).Error("Comment processing failed")

		// Обновляем статус на "ошибка"
		if updateErr := u.taskRepo.UpdateTaskStatus(ctx, taskID, tasks.StatusFailed, nil, err.Error()); updateErr != nil {
			log.WithError(updateErr).Error("Failed to update task status to failed")
		}

		return fmt.Errorf("process comments: %w", err)
	}

	// Обновляем статус на "завершено" с результатом
	if err := u.taskRepo.UpdateTaskStatus(ctx, taskID, tasks.StatusCompleted, result, ""); err != nil {
		log.WithError(err).Error("Failed to update task status to completed")
		return fmt.Errorf("update task status: %w", err)
	}

	log.Info("Comment processing task completed successfully")
	return nil
}

// processComments выполняет основную логику обработки комментариев.
func (u *TaskProcessorUsecase) processComments(groupID, postID int64) (json.RawMessage, error) {
	// TODO: Реализовать реальную логику обработки комментариев
	// Здесь может быть:
	// 1. Получение комментариев из VK API
	// 2. Анализ комментариев (морфологический анализ, ключевые слова)
	// 3. Сохранение результатов в базу данных

	// Пока что возвращаем заглушку
	result := map[string]interface{}{
		"processed_at":   time.Now().UTC(),
		"group_id":       groupID,
		"post_id":        postID,
		"comments_count": 0, // TODO: реальное количество обработанных комментариев
		"status":         "completed",
	}

	resultJSON, err := json.Marshal(result)
	if err != nil {
		return nil, fmt.Errorf("marshal result: %w", err)
	}

	return json.RawMessage(resultJSON), nil
}

// ProcessTask обрабатывает задачу по типу.
func (u *TaskProcessorUsecase) ProcessTask(ctx context.Context, taskID, taskType string, payload json.RawMessage) error {
	log := logrus.WithFields(logrus.Fields{
		"task_id":   taskID,
		"task_type": taskType,
	})

	switch taskType {
	case "analyze_comment":
		return u.processAnalyzeCommentTask(ctx, taskID, payload)
	case "parse_comments":
		return u.processParseCommentsTask(ctx, taskID, payload)
	default:
		log.WithField("task_type", taskType).Error("Unknown task type")
		return fmt.Errorf("unknown task type: %s", taskType)
	}
}

// processAnalyzeCommentTask обрабатывает задачу анализа комментария.
func (u *TaskProcessorUsecase) processAnalyzeCommentTask(ctx context.Context, taskID string, payload json.RawMessage) error {
	var req struct {
		GroupID int64 `json:"group_id"`
		PostID  int64 `json:"post_id"`
	}

	if err := json.Unmarshal(payload, &req); err != nil {
		return fmt.Errorf("unmarshal payload: %w", err)
	}

	return u.ProcessCommentsTask(ctx, taskID, req.GroupID, req.PostID)
}

// processParseCommentsTask обрабатывает задачу парсинга комментариев.
func (u *TaskProcessorUsecase) processParseCommentsTask(ctx context.Context, taskID string, payload json.RawMessage) error {
	var req struct {
		GroupID int64 `json:"group_id"`
		PostID  int64 `json:"post_id"`
	}

	if err := json.Unmarshal(payload, &req); err != nil {
		return fmt.Errorf("unmarshal payload: %w", err)
	}

	return u.ProcessCommentsTask(ctx, taskID, req.GroupID, req.PostID)
}
