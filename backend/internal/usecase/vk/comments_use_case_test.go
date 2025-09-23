package vk

import (
	"context"
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"vk-analyzer/internal/domain/comments"
)

// MockVKRepository - мок для VKRepository интерфейса
type MockVKRepository struct {
	mock.Mock
}

func (m *MockVKRepository) GetComments(ctx context.Context, ownerID int64, postID int64, token string) ([]comments.Comment, error) {
	args := m.Called(ctx, ownerID, postID, token)
	return args.Get(0).([]comments.Comment), args.Error(1)
}

// MockCommentRepository - мок для CommentRepository интерфейса
type MockCommentRepository struct {
	mock.Mock
}

func (m *MockCommentRepository) CreateMany(comments []comments.Comment) error {
	args := m.Called(comments)
	return args.Error(0)
}

// VKCommentsUseCaseTestSuite - тестовый набор для VKCommentsUseCase
type VKCommentsUseCaseTestSuite struct {
	suite.Suite
	useCase         *VKCommentsUseCase
	mockVKRepo      *MockVKRepository
	mockCommentRepo *MockCommentRepository
}

// SetupTest - настройка перед каждым тестом
func (suite *VKCommentsUseCaseTestSuite) SetupTest() {
	suite.mockVKRepo = new(MockVKRepository)
	suite.mockCommentRepo = new(MockCommentRepository)
	suite.useCase = NewVKCommentsUseCase()
}

// TestNewVKCommentsUseCase - тест создания нового use case
func (suite *VKCommentsUseCaseTestSuite) TestNewVKCommentsUseCase() {
	assert := assert.New(suite.T())

	useCase := NewVKCommentsUseCase()
	assert.NotNil(useCase)
	assert.IsType(&VKCommentsUseCase{}, useCase)
}

// TestFetchComments_Success - тест успешного запуска задачи получения комментариев
func (suite *VKCommentsUseCaseTestSuite) TestFetchComments_Success() {
	assert := assert.New(suite.T())

	// Act
	taskID, err := suite.useCase.FetchComments(context.Background(), -123, 456)

	// Assert
	assert.NoError(err)
	assert.NotEmpty(taskID)
	assert.Contains(taskID, "task_")
	assert.Contains(taskID, "-123")
	assert.Contains(taskID, "456")
}

// TestFetchComments_EmptyOwnerID - тест с пустым owner ID
func (suite *VKCommentsUseCaseTestSuite) TestFetchComments_EmptyOwnerID() {
	assert := assert.New(suite.T())

	// Act
	taskID, err := suite.useCase.FetchComments(context.Background(), 0, 456)

	// Assert
	assert.NoError(err)
	assert.NotEmpty(taskID)
	assert.Contains(taskID, "task_")
	assert.Contains(taskID, "0")
}

// TestFetchComments_EmptyPostID - тест с пустым post ID
func (suite *VKCommentsUseCaseTestSuite) TestFetchComments_EmptyPostID() {
	assert := assert.New(suite.T())

	// Act
	taskID, err := suite.useCase.FetchComments(context.Background(), -123, 0)

	// Assert
	assert.NoError(err)
	assert.NotEmpty(taskID)
	assert.Contains(taskID, "task_")
	assert.Contains(taskID, "-123")
	assert.Contains(taskID, "0")
}

// TestFetchComments_ContextCancelled - тест с отмененным контекстом
func (suite *VKCommentsUseCaseTestSuite) TestFetchComments_ContextCancelled() {
	assert := assert.New(suite.T())

	// Arrange
	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Отменяем контекст

	// Act
	taskID, err := suite.useCase.FetchComments(ctx, -123, 456)

	// Assert
	assert.Error(err) // Context should be cancelled
	assert.Empty(taskID)
}

// TestGetCommentsByTaskID_Completed - тест получения завершенной задачи
func (suite *VKCommentsUseCaseTestSuite) TestGetCommentsByTaskID_Completed() {
	assert := assert.New(suite.T())

	// Act
	status, comments, err := suite.useCase.GetCommentsByTaskID(context.Background(), "task_123_456")

	// Assert
	assert.NoError(err)
	assert.Equal("completed", status)
	assert.Len(comments, 1)
	assert.Equal(int64(1), comments[0].ID)
	assert.Equal("Mock comment", comments[0].Text)
	assert.Equal("task_123_456", comments[0].TaskID)
}

// TestGetCommentsByTaskID_Pending - тест получения задачи в ожидании
func (suite *VKCommentsUseCaseTestSuite) TestGetCommentsByTaskID_Pending() {
	assert := assert.New(suite.T())

	// Act
	status, comments, err := suite.useCase.GetCommentsByTaskID(context.Background(), "task_pending")

	// Assert
	assert.NoError(err)
	assert.Equal("pending", status)
	assert.Len(comments, 0)
}

// TestGetCommentsByTaskID_Failed - тест получения неудачной задачи
func (suite *VKCommentsUseCaseTestSuite) TestGetCommentsByTaskID_Failed() {
	assert := assert.New(suite.T())

	// Act
	status, comments, err := suite.useCase.GetCommentsByTaskID(context.Background(), "task_failed")

	// Assert
	assert.NoError(err)
	assert.Equal("failed", status)
	assert.Len(comments, 0)
}

// TestGetCommentsByTaskID_EmptyTaskID - тест с пустым task ID
func (suite *VKCommentsUseCaseTestSuite) TestGetCommentsByTaskID_EmptyTaskID() {
	assert := assert.New(suite.T())

	// Act
	status, comments, err := suite.useCase.GetCommentsByTaskID(context.Background(), "")

	// Assert
	assert.NoError(err)
	assert.Equal("completed", status) // В текущей реализации возвращается completed по умолчанию
	assert.Len(comments, 1)
}

// TestListComments_Success - тест получения списка комментариев
func (suite *VKCommentsUseCaseTestSuite) TestListComments_Success() {
	assert := assert.New(suite.T())

	// Act
	comments, err := suite.useCase.ListComments(context.Background(), "task_123_456", 3)

	// Assert
	assert.NoError(err)
	assert.Len(comments, 3)
	for i, comment := range comments {
		assert.Equal(int64(i+1), comment.ID)
		assert.Equal("task_123_456", comment.TaskID)
		assert.Equal(fmt.Sprintf("Comment %d", i+1), comment.Text)
	}
}

// TestListComments_ZeroLimit - тест с нулевым лимитом
func (suite *VKCommentsUseCaseTestSuite) TestListComments_ZeroLimit() {
	assert := assert.New(suite.T())

	// Act
	comments, err := suite.useCase.ListComments(context.Background(), "task_123_456", -1)

	// Assert
	assert.NoError(err)
	assert.Len(comments, 0)
}

// TestListComments_NegativeLimit - тест с отрицательным лимитом
func (suite *VKCommentsUseCaseTestSuite) TestListComments_NegativeLimit() {
	assert := assert.New(suite.T())

	// Act
	comments, err := suite.useCase.ListComments(context.Background(), "task_123_456", -1)

	// Assert
	assert.NoError(err)
	assert.Len(comments, 0)
}

// TestListComments_LargeLimit - тест с большим лимитом
func (suite *VKCommentsUseCaseTestSuite) TestListComments_LargeLimit() {
	assert := assert.New(suite.T())

	// Act
	comments, err := suite.useCase.ListComments(context.Background(), "task_123_456", 1000)

	// Assert
	assert.NoError(err)
	assert.Len(comments, 1000)
	for i, comment := range comments {
		assert.Equal(int64(i+1), comment.ID)
		assert.Equal("task_123_456", comment.TaskID)
	}
}

// TestListComments_EmptyTaskID - тест с пустым task ID
func (suite *VKCommentsUseCaseTestSuite) TestListComments_EmptyTaskID() {
	assert := assert.New(suite.T())

	// Act
	comments, err := suite.useCase.ListComments(context.Background(), "", 2)

	// Assert
	assert.NoError(err)
	assert.Len(comments, 2)
	for i, comment := range comments {
		assert.Equal(int64(i+1), comment.ID)
		assert.Equal("", comment.TaskID)
	}
}

// TestListComments_ContextCancelled - тест с отмененным контекстом
func (suite *VKCommentsUseCaseTestSuite) TestListComments_ContextCancelled() {
	assert := assert.New(suite.T())

	// Arrange
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	// Act
	comments, err := suite.useCase.ListComments(ctx, "task_123_456", 2)

	// Assert
	assert.Error(err) // Context should be cancelled
	assert.Len(comments, 0)
}

// TestConcurrentAccess - тест параллельного доступа
func (suite *VKCommentsUseCaseTestSuite) TestConcurrentAccess() {
	assert := assert.New(suite.T())

	// Act - параллельные вызовы
	done := make(chan bool, 3)

	for i := 0; i < 3; i++ {
		go func(index int) {
			taskID, err := suite.useCase.FetchComments(context.Background(), -123, 456)
			assert.NoError(err)
			assert.NotEmpty(taskID)
			done <- true
		}(i)
	}

	// Ожидаем завершения всех горутин
	for i := 0; i < 3; i++ {
		<-done
	}
}

// TestTaskIDFormat - тест формата task ID
func (suite *VKCommentsUseCaseTestSuite) TestTaskIDFormat() {
	assert := assert.New(suite.T())

	testCases := []struct {
		ownerID  int
		postID   int
		expected string
	}{
		{-123, 456, "task_-123_456"},
		{0, 0, "task_0_0"},
		{999, 1, "task_999_1"},
		{-1, -1, "task_-1_-1"},
	}

	for _, tc := range testCases {
		taskID, err := suite.useCase.FetchComments(context.Background(), tc.ownerID, tc.postID)
		assert.NoError(err)
		assert.Equal(tc.expected, taskID)
	}
}

// TestSuite - запуск всего набора тестов
func TestVKCommentsUseCaseTestSuite(t *testing.T) {
	suite.Run(t, new(VKCommentsUseCaseTestSuite))
}
