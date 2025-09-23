package main

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"github.com/hibiken/asynq"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"gorm.io/gorm"
	"vk-analyzer/internal/domain/comments"
	"vk-analyzer/internal/domain/morphological"
	"vk-analyzer/internal/repository/postgres"
	"vk-analyzer/internal/repository/vk"
)

type MockRedisClient struct {
	mock.Mock
}

func (m *MockRedisClient) Get(ctx context.Context, key string) *redis.StringCmd {
	args := m.Called(ctx, key)
	return args.Get(0).(*redis.StringCmd)
}

type MockStringCmd struct {
	mock.Mock
}

func (m *MockStringCmd) Result() (string, error) {
	args := m.Called()
	return args.String(0), args.Error(1)
}

type MockGORMDB struct {
	mock.Mock
}

func (m *MockGORMDB) Open(driverName string, config *gorm.Config) (*gorm.DB, error) {
	args := m.Called(driverName, config)
	return args.Get(0).(*gorm.DB), args.Error(1)
}

type MockCommentRepository struct {
	mock.Mock
}

func (m *MockCommentRepository) CreateMany(comments []comments.Comment) error {
	args := m.Called(comments)
	return args.Error(0)
}

func (m *MockCommentRepository) GetByID(id int64) (*comments.Comment, error) {
	args := m.Called(id)
	return args.Get(0).(*comments.Comment), args.Error(1)
}

func (m *MockCommentRepository) Update(comment *comments.Comment) error {
	args := m.Called(comment)
	return args.Error(0)
}

type MockAsynqClient struct {
	mock.Mock
}

func (m *MockAsynqClient) Enqueue(task *asynq.Task) (*asynq.TaskID, error) {
	args := m.Called(task)
	return args.Get(0).(*asynq.TaskID), args.Error(1)
}

type MockVKRepository struct {
	mock.Mock
}

func (m *MockVKRepository) GetComments(ctx context.Context, ownerID, postID int64, token string) ([]vk.VKComment, error) {
	args := m.Called(ctx, ownerID, postID, token)
	return args.Get(0).([]vk.VKComment), args.Error(1)
}

func TestHandleFetchComments_ValidPayload(t *testing.T) {
	// Arrange
	ctx := context.Background()
	payload, _ := json.Marshal(FetchCommentsPayload{
		OwnerID: -123,
		PostID:  456,
		TaskID:  "test_task",
	})
	task := asynq.NewTask("vk:fetch_comments", payload)

	mockRedis := &MockRedisClient{}
	mockStringCmd := &MockStringCmd{}
	mockRedis.On("Get", ctx, "token:test_task").Return(mockStringCmd)
	mockStringCmd.On("Result").Return("test_token", nil)

	mockVKRepo := &MockVKRepository{}
	mockVKRepo.On("GetComments", ctx, int64(-123), int64(456), "test_token").Return([]vk.VKComment{
		{ID: 1, FromID: 789, Text: "Test VK comment", Likes: 10},
	}, nil)

	mockDB := &MockGORMDB{}
	mockCommentRepo := &MockCommentRepository{}
	mockDB.On("Open", mock.Anything, mock.Anything).Return(&gorm.DB{}, nil)
	mockCommentRepo.On("CreateMany", mock.Anything).Return(nil)

	mockAsynqClient := &MockAsynqClient{}
	mockAsynqClient.On("Enqueue", mock.Anything).Return(&asynq.TaskID{}, nil)

	// Для переопределения зависимостей в тесте (в реальности DI)
	originalNewCommentRepository := newCommentRepository
	newCommentRepository = func(db *gorm.DB) postgres.CommentRepository {
		return mockCommentRepo
	}
	defer func() { newCommentRepository = originalNewCommentRepository }()

	// Act
	err := HandleFetchComments(ctx, task)

	// Assert
	assert.NoError(t, err)
	mockRedis.AssertExpectations(t)
	mockStringCmd.AssertExpectations(t)
	mockVKRepo.AssertExpectations(t)
	mockDB.AssertExpectations(t)
	mockCommentRepo.AssertExpectations(t)
	mockAsynqClient.AssertExpectations(t)
}

func TestHandleFetchComments_InvalidPayload(t *testing.T) {
	// Arrange
	ctx := context.Background()
	invalidPayload := []byte(`{"owner_id":"invalid","post_id":456}`)
	task := asynq.NewTask("vk:fetch_comments", invalidPayload)

	// Act
	err := HandleFetchComments(ctx, task)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to unmarshal payload")
}

func TestHandleFetchComments_RedisError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	payload, _ := json.Marshal(FetchCommentsPayload{
		OwnerID: -123,
		PostID:  456,
		TaskID:  "test_task",
	})
	task := asynq.NewTask("vk:fetch_comments", payload)

	mockRedis := &MockRedisClient{}
	mockStringCmd := &MockStringCmd{}
	mockRedis.On("Get", ctx, "token:test_task").Return(mockStringCmd)
	mockStringCmd.On("Result").Return("", errors.New("redis connection error"))

	// Act
	err := HandleFetchComments(ctx, task)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to get token from Redis")
	mockRedis.AssertExpectations(t)
	mockStringCmd.AssertExpectations(t)
}

func TestHandleFetchComments_VKError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	payload, _ := json.Marshal(FetchCommentsPayload{
		OwnerID: -123,
		PostID:  456,
		TaskID:  "test_task",
	})
	task := asynq.NewTask("vk:fetch_comments", payload)

	mockRedis := &MockRedisClient{}
	mockStringCmd := &MockStringCmd{}
	mockRedis.On("Get", ctx, "token:test_task").Return(mockStringCmd)
	mockStringCmd.On("Result").Return("test_token", nil)

	mockVKRepo := &MockVKRepository{}
	mockVKRepo.On("GetComments", ctx, int64(-123), int64(456), "test_token").Return(nil, errors.New("VK API error"))

	// Act
	err := HandleFetchComments(ctx, task)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to fetch comments from VK")
	mockRedis.AssertExpectations(t)
	mockStringCmd.AssertExpectations(t)
	mockVKRepo.AssertExpectations(t)
}

func TestHandleFetchComments_DBSaveError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	payload, _ := json.Marshal(FetchCommentsPayload{
		OwnerID: -123,
		PostID:  456,
		TaskID:  "test_task",
	})
	task := asynq.NewTask("vk:fetch_comments", payload)

	mockRedis := &MockRedisClient{}
	mockStringCmd := &MockStringCmd{}
	mockRedis.On("Get", ctx, "token:test_task").Return(mockStringCmd)
	mockStringCmd.On("Result").Return("test_token", nil)

	mockVKRepo := &MockVKRepository{}
	mockVKRepo.On("GetComments", ctx, int64(-123), int64(456), "test_token").Return([]vk.VKComment{
		{ID: 1, FromID: 789, Text: "Test", Likes: 10},
	}, nil)

	mockDB := &MockGORMDB{}
	mockCommentRepo := &MockCommentRepository{}
	mockDB.On("Open", mock.Anything, mock.Anything).Return(&gorm.DB{}, nil)
	mockCommentRepo.On("CreateMany", mock.Anything).Return(errors.New("DB save error"))

	// Для переопределения
	originalNewCommentRepository := newCommentRepository
	newCommentRepository = func(db *gorm.DB) postgres.CommentRepository {
		return mockCommentRepo
	}
	defer func() { newCommentRepository = originalNewCommentRepository }()

	// Act
	err := HandleFetchComments(ctx, task)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to save comments")
	mockRedis.AssertExpectations(t)
	mockStringCmd.AssertExpectations(t)
	mockVKRepo.AssertExpectations(t)
	mockDB.AssertExpectations(t)
	mockCommentRepo.AssertExpectations(t)
}

func TestHandleAnalyze_ValidPayload(t *testing.T) {
	// Arrange
	ctx := context.Background()
	payload, _ := json.Marshal(AnalyzePayload{
		CommentIDs: []int64{1, 2},
		TaskID:     "test_task",
	})
	task := asynq.NewTask("morphological:analyze", payload)

	mockCommentRepo := &MockCommentRepository{}
	mockCommentRepo.On("GetByID", int64(1)).Return(&comments.Comment{ID: 1, Text: "Test text"}, nil)
	mockCommentRepo.On("Update", mock.Anything).Return(nil)

	mockDB := &MockGORMDB{}
	mockDB.On("Open", mock.Anything, mock.Anything).Return(&gorm.DB{}, nil)

	// Mock morphological.AnalyzeText
	originalAnalyzeText := morphological.AnalyzeText
	morphological.AnalyzeText = func(text string) morphological.Analysis {
		return morphological.Analysis{
			Keywords: []string{"test", "keyword"},
			Sentiment: "positive",
		}
	}
	defer func() { morphological.AnalyzeText = originalAnalyzeText }()

	// Для переопределения
	originalNewCommentRepository := newCommentRepository
	newCommentRepository = func(db *gorm.DB) postgres.CommentRepository {
		return mockCommentRepo
	}
	defer func() { newCommentRepository = originalNewCommentRepository }()

	// Act
	err := HandleAnalyze(ctx, task)

	// Assert
	assert.NoError(t, err)
	mockCommentRepo.AssertExpectations(t)
	mockDB.AssertExpectations(t)
}

func TestHandleAnalyze_DBGetError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	payload, _ := json.Marshal(AnalyzePayload{
		CommentIDs: []int64{1},
		TaskID:     "test_task",
	})
	task := asynq.NewTask("morphological:analyze", payload)

	mockCommentRepo := &MockCommentRepository{}
	mockCommentRepo.On("GetByID", int64(1)).Return(nil, errors.New("DB get error"))

	mockDB := &MockGORMDB{}
	mockDB.On("Open", mock.Anything, mock.Anything).Return(&gorm.DB{}, nil)

	// Для переопределения
	originalNewCommentRepository := newCommentRepository
	newCommentRepository = func(db *gorm.DB) postgres.CommentRepository {
		return mockCommentRepo
	}
	defer func() { newCommentRepository = originalNewCommentRepository }()

	// Act
	err := HandleAnalyze(ctx, task)

	// Assert
	assert.NoError(t, err) // Logs error but continues
	mockCommentRepo.AssertExpectations(t)
	mockDB.AssertExpectations(t)
}

func TestHandleAnalyze_UpdateError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	payload, _ := json.Marshal(AnalyzePayload{
		CommentIDs: []int64{1},
		TaskID:     "test_task",
	})
	task := asynq.NewTask("morphological:analyze", payload)

	mockCommentRepo := &MockCommentRepository{}
	mockCommentRepo.On("GetByID", int64(1)).Return(&comments.Comment{ID: 1, Text: "Test"}, nil)
	mockCommentRepo.On("Update", mock.Anything).Return(errors.New("update error"))

	mockDB := &MockGORMDB{}
	mockDB.On("Open", mock.Anything, mock.Anything).Return(&gorm.DB{}, nil)

	// Mock morphological.AnalyzeText
	originalAnalyzeText := morphological.AnalyzeText
	morphological.AnalyzeText = func(text string) morphological.Analysis {
		return morphological.Analysis{
			Keywords: []string{"test"},
			Sentiment: "positive",
		}
	}
	defer func() { morphological.AnalyzeText = originalAnalyzeText }()

	// Для переопределения
	originalNewCommentRepository := newCommentRepository
	newCommentRepository = func(db *gorm.DB) postgres.CommentRepository {
		return mockCommentRepo
	}
	defer func() { newCommentRepository = originalNewCommentRepository }()

	// Act
	err := HandleAnalyze(ctx, task)

	// Assert
	assert.NoError(t, err) // Logs error but continues
	mockCommentRepo.AssertExpectations(t)
	mockDB.AssertExpectations(t)
}
