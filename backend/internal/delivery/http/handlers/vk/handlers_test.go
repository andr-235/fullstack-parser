package vk

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"vk-analyzer/internal/domain/comments"
	"vk-analyzer/internal/usecase/vk"
)

type MockVKCommentsUseCase struct {
	mock.Mock
}

func (m *MockVKCommentsUseCase) FetchComments(ctx context.Context, ownerID, postID int) (string, error) {
	args := m.Called(ctx, ownerID, postID)
	return args.String(0), args.Error(1)
}

func (m *MockVKCommentsUseCase) GetCommentsByTaskID(ctx context.Context, taskID string) (string, []comments.Comment, error) {
	args := m.Called(ctx, taskID)
	return args.String(0), args.Get(1).([]comments.Comment), args.Error(2)
}

func (m *MockVKCommentsUseCase) ListComments(ctx context.Context, taskID string, limit int) ([]comments.Comment, error) {
	args := m.Called(ctx, taskID, limit)
	return args.Get(0).([]comments.Comment), args.Error(1)
}

func setupRouter(mockUC *MockVKCommentsUseCase) *gin.Engine {
	r := gin.Default()
	h := NewVKHandler(mockUC)
	r.POST("/api/vk/fetch-comments", h.FetchComments)
	r.GET("/api/vk/task/:task_id", h.TaskStatus)
	r.GET("/api/comments", h.ListComments)
	return r
}

func TestFetchComments_ValidRequest(t *testing.T) {
	// Arrange
	mockUC := &MockVKCommentsUseCase{}
	expectedTaskID := "test_task_id"
	mockUC.On("FetchComments", mock.Anything, int64(123), int64(456)).Return(expectedTaskID, nil)

	r := setupRouter(mockUC)
	body := []byte(`{"owner_id":123,"post_id":456}`)
	req, _ := http.NewRequest("POST", "/api/vk/fetch-comments", bytes.NewReader(body))
	w := httptest.NewRecorder()
	ctx, _ := gin.CreateTestContext(w)
	ctx.Request = req

	// Act
	h := NewVKHandler(mockUC)
	h.FetchComments(ctx)

	// Assert
	assert.Equal(t, http.StatusOK, w.Code)
	var resp map[string]interface{}
	json.NewDecoder(bytes.NewReader(w.Body.Bytes())).Decode(&resp)
	assert.Equal(t, expectedTaskID, resp["task_id"])
	mockUC.AssertExpectations(t)
}

func TestFetchComments_InvalidJSON(t *testing.T) {
	// Arrange
	mockUC := &MockVKCommentsUseCase{}
	r := setupRouter(mockUC)
	body := []byte(`{"owner_id":"invalid","post_id":456}`)
	req, _ := http.NewRequest("POST", "/api/vk/fetch-comments", bytes.NewReader(body))
	w := httptest.NewRecorder()
	ctx, _ := gin.CreateTestContext(w)
	ctx.Request = req

	// Act
	h := NewVKHandler(mockUC)
	h.FetchComments(ctx)

	// Assert
	assert.Equal(t, http.StatusBadRequest, w.Code)
	var resp map[string]interface{}
	json.NewDecoder(bytes.NewReader(w.Body.Bytes())).Decode(&resp)
	assert.Contains(t, resp["error"], "Invalid request body")
	mockUC.AssertNotCalled(t, "FetchComments")
}

func TestFetchComments_UseCaseError(t *thinking>
	// Arrange
	mockUC := &MockVKCommentsUseCase{}
	mockUC.On("FetchComments", mock.Anything, int64(123), int64(456)).Return("", errors.New("use case error"))

	r := setupRouter(mockUC)
	body, _ := json.Marshal(map[string]int{"owner_id":123,"post_id":456})
	req, _ := http.NewRequest("POST", "/api/vk/fetch-comments", bytes.NewReader(body))
	w := httptest.NewRecorder()
	ctx, _ := gin.CreateTestContext(w)
	ctx.Request = req

	// Act
	h := NewVKHandler(mockUC)
	h.FetchComments(ctx)

	// Assert
	assert.Equal(t, http.StatusInternalServerError, w.Code)
	var resp map[string]interface{}
	json.NewDecoder(bytes.NewReader(w.Body.Bytes())).Decode(&resp)
	assert.Contains(t, resp["error"], "Failed to fetch comments")
	mockUC.AssertExpectations(t)
</thinking>

