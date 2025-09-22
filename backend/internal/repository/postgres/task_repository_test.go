package postgres

import (
	"context"
	"encoding/json"
	"testing"

	"backend/internal/domain/tasks"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func setupTestDB(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err)

	// Создаем таблицу
	err = db.AutoMigrate(&TaskModel{})
	require.NoError(t, err)

	return db
}

func TestTaskRepository_Enqueue(t *testing.T) {
	db := setupTestDB(t)
	repo := NewTaskRepository(db)
	ctx := context.Background()

	payload := json.RawMessage(`{"group_id": 123, "post_id": 456}`)
	req := &tasks.EnqueueRequest{
		Type:    "analyze_comment",
		Payload: payload,
	}

	taskID, err := repo.Enqueue(ctx, req)
	assert.NoError(t, err)
	assert.NotEmpty(t, taskID)

	// Проверяем, что задача сохранилась
	var task TaskModel
	err = db.Where("id = ?", taskID).First(&task).Error
	assert.NoError(t, err)
	assert.Equal(t, "analyze_comment", task.Type)
	assert.Equal(t, string(tasks.StatusPending), task.Status)
}

func TestTaskRepository_GetTask(t *testing.T) {
	db := setupTestDB(t)
	repo := NewTaskRepository(db)
	ctx := context.Background()

	// Создаем тестовую задачу
	payload := json.RawMessage(`{"test": "data"}`)
	req := &tasks.EnqueueRequest{
		Type:    "test_task",
		Payload: payload,
	}

	taskID, err := repo.Enqueue(ctx, req)
	require.NoError(t, err)

	// Получаем задачу
	task, err := repo.GetTask(ctx, taskID)
	assert.NoError(t, err)
	assert.Equal(t, taskID, task.ID)
	assert.Equal(t, tasks.StatusPending, task.Status)
}

func TestTaskRepository_CancelTask(t *testing.T) {
	db := setupTestDB(t)
	repo := NewTaskRepository(db)
	ctx := context.Background()

	// Создаем тестовую задачу
	payload := json.RawMessage(`{"test": "data"}`)
	req := &tasks.EnqueueRequest{
		Type:    "test_task",
		Payload: payload,
	}

	taskID, err := repo.Enqueue(ctx, req)
	require.NoError(t, err)

	// Отменяем задачу
	err = repo.CancelTask(ctx, taskID)
	assert.NoError(t, err)

	// Проверяем статус
	task, err := repo.GetTask(ctx, taskID)
	assert.NoError(t, err)
	assert.Equal(t, tasks.StatusCanceled, task.Status)
}

func TestTaskRepository_ListTasks(t *testing.T) {
	db := setupTestDB(t)
	repo := NewTaskRepository(db)
	ctx := context.Background()

	// Создаем несколько тестовых задач
	for i := 0; i < 5; i++ {
		payload := json.RawMessage(`{"test": "data"}`)
		req := &tasks.EnqueueRequest{
			Type:    "test_task",
			Payload: payload,
		}
		_, err := repo.Enqueue(ctx, req)
		require.NoError(t, err)
	}

	// Получаем список задач
	listReq := &tasks.ListRequest{
		Page:  1,
		Limit: 3,
	}

	resp, err := repo.ListTasks(ctx, listReq)
	assert.NoError(t, err)
	assert.Equal(t, int64(5), resp.Total)
	assert.Equal(t, 3, len(resp.Tasks))
	assert.Equal(t, 1, resp.Page)
	assert.Equal(t, 3, resp.Limit)
}

func TestTaskRepository_UpdateTaskStatus(t *testing.T) {
	db := setupTestDB(t)
	repo := NewTaskRepository(db)
	ctx := context.Background()

	// Создаем тестовую задачу
	payload := json.RawMessage(`{"test": "data"}`)
	req := &tasks.EnqueueRequest{
		Type:    "test_task",
		Payload: payload,
	}

	taskID, err := repo.Enqueue(ctx, req)
	require.NoError(t, err)

	// Обновляем статус
	result := json.RawMessage(`{"result": "success"}`)
	err = repo.UpdateTaskStatus(ctx, taskID, tasks.StatusCompleted, result, "")
	assert.NoError(t, err)

	// Проверяем обновление
	task, err := repo.GetTask(ctx, taskID)
	assert.NoError(t, err)
	assert.Equal(t, tasks.StatusCompleted, task.Status)
	assert.JSONEq(t, string(result), string(task.Result))
}

func TestTaskRepository_GetStats(t *testing.T) {
	db := setupTestDB(t)
	repo := NewTaskRepository(db)
	ctx := context.Background()

	// Создаем задачи с разными статусами
	statuses := []tasks.Status{
		tasks.StatusPending,
		tasks.StatusPending,
		tasks.StatusActive,
		tasks.StatusCompleted,
		tasks.StatusFailed,
	}

	for _, status := range statuses {
		payload := json.RawMessage(`{"test": "data"}`)
		req := &tasks.EnqueueRequest{
			Type:    "test_task",
			Payload: payload,
		}
		taskID, err := repo.Enqueue(ctx, req)
		require.NoError(t, err)

		if status != tasks.StatusPending {
			err = repo.UpdateTaskStatus(ctx, taskID, status, nil, "")
			require.NoError(t, err)
		}
	}

	// Получаем статистику
	stats, err := repo.GetStats(ctx)
	assert.NoError(t, err)
	assert.Equal(t, 2, stats.Pending)
	assert.Equal(t, 1, stats.Active)
	assert.Equal(t, 1, stats.Completed)
	assert.Equal(t, 1, stats.Failed)
	assert.Equal(t, 0, stats.Canceled)
}
