package tasks

import (
	"context"
	"errors"
	"strings"

	"github.com/sirupsen/logrus"
	"backend/internal/domain/tasks"
	redis "backend/internal/repository/redis"
)

// TasksUsecase - use case для управления задачами.
type TasksUsecase struct {
	repo redis.TaskRepository
}

// NewTasksUsecase создает новый use case для задач.
func NewTasksUsecase(repo redis.TaskRepository) *TasksUsecase {
	return &TasksUsecase{repo: repo}
}

// EnqueueTask постановка задачи в очередь.
func (u *TasksUsecase) EnqueueTask(ctx context.Context, req *tasks.EnqueueRequest) (string, error) {
	// Валидация типа задачи
	validTypes := []string{"analyze_comment"} // TODO: добавить другие типы
	if !contains(validTypes, req.Type) {
		logrus.WithField("type", req.Type).Error("Недопустимый тип задачи")
		return "", errors.New("недопустимый тип задачи")
	}

	// Валидация payload (простая, для JSON)
	if len(req.Payload) == 0 {
		return "", errors.New("payload не может быть пустым")
	}

	id, err := u.repo.Enqueue(ctx, req)
	if err != nil {
		logrus.WithError(err).Error("Ошибка постановки задачи")
		return "", err
	}

	logrus.WithField("task_id", id).Info("Задача поставлена в очередь через use case")
	return id, nil
}

// GetTaskStatus получение статуса задачи.
func (u *TasksUsecase) GetTaskStatus(ctx context.Context, id string) (*tasks.TaskResponse, error) {
	if id == "" {
		return nil, errors.New("ID задачи не может быть пустым")
	}

	resp, err := u.repo.GetTask(ctx, id)
	if err != nil {
		logrus.WithError(err).WithField("task_id", id).Error("Ошибка получения статуса задачи")
		if strings.Contains(err.Error(), "не найдена") {
			return nil, err
		}
		return nil, err
	}

	return resp, nil
}

// CancelTask отмена задачи.
func (u *TasksUsecase) CancelTask(ctx context.Context, id string) error {
	if id == "" {
		return errors.New("ID задачи не может быть пустым")
	}

	err := u.repo.CancelTask(ctx, id)
	if err != nil {
		logrus.WithError(err).WithField("task_id", id).Error("Ошибка отмены задачи")
		return err
	}

	logrus.WithField("task_id", id).Info("Задача отменена через use case")
	return nil
}

// ListTasks список задач с фильтрацией.
func (u *TasksUsecase) ListTasks(ctx context.Context, req *tasks.ListRequest) (*tasks.ListResponse, error) {
	if req.Limit == 0 {
		req.Limit = 10
	}
	if req.Page == 0 {
		req.Page = 1
	}

	resp, err := u.repo.ListTasks(ctx, req)
	if err != nil {
		logrus.WithError(err).Error("Ошибка получения списка задач")
		return nil, err
	}

	logrus.WithFields(logrus.Fields{
		"page":  req.Page,
		"limit": req.Limit,
		"total": resp.Total,
	}).Info("Список задач получен")
	return resp, nil
}

// GetStats получение статистики очередей.
func (u *TasksUsecase) GetStats(ctx context.Context) (*tasks.StatsResponse, error) {
	stats, err := u.repo.GetStats(ctx)
	if err != nil {
		logrus.WithError(err).Error("Ошибка получения статистики")
		return nil, err
	}

	logrus.Info("Статистика получена через use case")
	return stats, nil
}

// contains проверяет наличие строки в слайсе.
func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}