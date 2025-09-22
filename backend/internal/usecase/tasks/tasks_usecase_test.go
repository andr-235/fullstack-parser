package tasks

import (
	"context"
	"errors"
	"testing"

	"backend/internal/domain/tasks"

	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockTaskRepository struct {
	mock.Mock
}

func (m *MockTaskRepository) Enqueue(ctx context.Context, req *tasks.EnqueueRequest) (string, error) {
	args := m.Called(ctx, req)
	return args.String(0), args.Error(1)
}

func (m *MockTaskRepository) GetTask(ctx context.Context, id string) (*tasks.TaskResponse, error) {
	args := m.Called(ctx, id)
	return args.Get(0).(*tasks.TaskResponse), args.Error(1)
}

func (m *MockTaskRepository) CancelTask(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockTaskRepository) ListTasks(ctx context.Context, req *tasks.ListRequest) (*tasks.ListResponse, error) {
	args := m.Called(ctx, req)
	return args.Get(0).(*tasks.ListResponse), args.Error(1)
}

func (m *MockTaskRepository) GetStats(ctx context.Context) (*tasks.StatsResponse, error) {
	args := m.Called(ctx)
	return args.Get(0).(*tasks.StatsResponse), args.Error(1)
}

func TestTasksUsecase_EnqueueTask_Success(t *testing.T) {
	mockRepo := new(MockTaskRepository)
	uc := NewTasksUsecase(mockRepo)

	ctx := context.Background()
	req := &tasks.EnqueueRequest{
		Type:    "analyze_comment",
		Payload: []byte(`{"comment_id": "123"}`),
	}
	expectedID := "task123"
	mockRepo.On("Enqueue", ctx, req).Return(expectedID, nil)

	id, err := uc.EnqueueTask(ctx, req)

	assert.NoError(t, err)
	assert.Equal(t, expectedID, id)
	mockRepo.AssertExpectations(t)
}

func TestTasksUsecase_EnqueueTask_InvalidType(t *testing.T) {
	mockRepo := new(MockTaskRepository)
	uc := NewTasksUsecase(mockRepo)

	ctx := context.Background()
	req := &tasks.EnqueueRequest{
		Type:    "invalid_type",
		Payload: []byte(`{}`),
	}

	id, err := uc.EnqueueTask(ctx, req)

	assert.Error(t, err)
	assert.Equal(t, "недопустимый тип задачи", err.Error())
	assert.Empty(t, id)
	mockRepo.AssertNotCalled(t, "Enqueue")
}

func TestTasksUsecase_GetTaskStatus_Success(t *testing.T) {
	mockRepo := new(MockTaskRepository)
	uc := NewTasksUsecase(mockRepo)

	ctx := context.Background()
	id := "task123"
	expectedResp := &tasks.TaskResponse{ID: id, Status: tasks.StatusCompleted}
	mockRepo.On("GetTask", ctx, id).Return(expectedResp, nil)

	resp, err := uc.GetTaskStatus(ctx, id)

	assert.NoError(t, err)
	assert.Equal(t, expectedResp, resp)
	mockRepo.AssertExpectations(t)
}

func TestTasksUsecase_GetTaskStatus_EmptyID(t *testing.T) {
	mockRepo := new(MockTaskRepository)
	uc := NewTasksUsecase(mockRepo)

	ctx := context.Background()
	id := ""
	_, err := uc.GetTaskStatus(ctx, id)

	assert.Error(t, err)
	assert.Equal(t, "ID задачи не может быть пустым", err.Error())
	mockRepo.AssertNotCalled(t, "GetTask")
}

func TestTasksUsecase_CancelTask_Success(t *testing.T) {
	mockRepo := new(MockTaskRepository)
	uc := NewTasksUsecase(mockRepo)

	ctx := context.Background()
	id := "task123"
	mockRepo.On("CancelTask", ctx, id).Return(nil)

	err := uc.CancelTask(ctx, id)

	assert.NoError(t, err)
	mockRepo.AssertExpectations(t)
}

func TestTasksUsecase_ListTasks_Success(t *testing.T) {
	mockRepo := new(MockTaskRepository)
	uc := NewTasksUsecase(mockRepo)

	ctx := context.Background()
	req := &tasks.ListRequest{Page: 1, Limit: 10}
	expectedResp := &tasks.ListResponse{Total: 5}
	mockRepo.On("ListTasks", ctx, req).Return(expectedResp, nil)

	resp, err := uc.ListTasks(ctx, req)

	assert.NoError(t, err)
	assert.Equal(t, expectedResp, resp)
	mockRepo.AssertExpectations(t)
}

func TestTasksUsecase_GetStats_Success(t *testing.T) {
	mockRepo := new(MockTaskRepository)
	uc := NewTasksUsecase(mockRepo)

	ctx := context.Background()
	expectedStats := &tasks.StatsResponse{Pending: 1}
	mockRepo.On("GetStats", ctx).Return(expectedStats, nil)

	stats, err := uc.GetStats(ctx)

	assert.NoError(t, err)
	assert.Equal(t, expectedStats, stats)
	mockRepo.AssertExpectations(t)
}