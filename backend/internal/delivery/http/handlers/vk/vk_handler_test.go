package vk

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"vk-analyzer/internal/domain/comments"
	"vk-analyzer/internal/usecase/vk"
)

// MockVKCommentsUseCase - мок для VKCommentsUseCase интерфейса
type MockVKCommentsUseCase struct {
	mock.Mock
}

func (m *MockVKCommentsUseCase) FetchComments(ctx context.Context, ownerID, postID int64) (string, error) {
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

// MockGinContext - мок для gin.Context
type MockGinContext struct {
	mock.Mock
}

func (m *MockGinContext) ShouldBindJSON(obj interface{}) error {
	args := m.Called(obj)
	return args.Error(0)
}

func (m *MockGinContext) JSON(code int, obj interface{}) {
	m.Called(code, obj)
}

func (m *MockGinContext) Param(key string) string {
	args := m.Called(key)
	return args.String(0)
}

func (m *MockGinContext) Query(key string) string {
	args := m.Called(key)
	return args.String(0)
}

func (m *MockGinContext) Request() *http.Request {
	args := m.Called()
	return args.Get(0).(*http.Request)
}

func TestVKHandler_FetchComments_Success(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	expectedTaskID := "task-123"
	mockUC.On("FetchComments", mock.Anything, int64(123), int64(456)).Return(expectedTaskID, nil)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	requestBody := map[string]int{
		"owner_id": 123,
		"post_id":  456,
	}
	jsonBody, _ := json.Marshal(requestBody)
	c.Request = httptest.NewRequest("POST", "/api/vk/fetch-comments", bytes.NewBuffer(jsonBody))
	c.Request.Header.Set("Content-Type", "application/json")

	// Act
	handler.FetchComments(c)

	// Assert
	assert.Equal(t, http.StatusOK, w.Code)
	var response map[string]string
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, expectedTaskID, response["task_id"])
	mockUC.AssertExpectations(t)
}

func TestVKHandler_FetchComments_InvalidJSON(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	c.Request = httptest.NewRequest("POST", "/api/vk/fetch-comments", bytes.NewBufferString("invalid json"))
	c.Request.Header.Set("Content-Type", "application/json")

	// Act
	handler.FetchComments(c)

	// Assert
	assert.Equal(t, http.StatusBadRequest, w.Code)
	var response map[string]string
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Contains(t, response["error"], "Invalid request body")
	mockUC.AssertNotCalled(t, "FetchComments", mock.Anything, mock.Anything, mock.Anything)
}

func TestVKHandler_FetchComments_MissingFields(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	requestBody := map[string]int{
		"owner_id": 123,
		// missing post_id
	}
	jsonBody, _ := json.Marshal(requestBody)
	c.Request = httptest.NewRequest("POST", "/api/vk/fetch-comments", bytes.NewBuffer(jsonBody))
	c.Request.Header.Set("Content-Type", "application/json")

	// Act
	handler.FetchComments(c)

	// Assert
	assert.Equal(t, http.StatusBadRequest, w.Code)
	var response map[string]string
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Contains(t, response["error"], "Invalid request body")
	mockUC.AssertNotCalled(t, "FetchComments", mock.Anything, mock.Anything, mock.Anything)
}

func TestVKHandler_FetchComments_UseCaseError(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	expectedError := errors.New("use case error")
	mockUC.On("FetchComments", mock.Anything, int64(123), int64(456)).Return("", expectedError)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	requestBody := map[string]int{
		"owner_id": 123,
		"post_id":  456,
	}
	jsonBody, _ := json.Marshal(requestBody)
	c.Request = httptest.NewRequest("POST", "/api/vk/fetch-comments", bytes.NewBuffer(jsonBody))
	c.Request.Header.Set("Content-Type", "application/json")

	// Act
	handler.FetchComments(c)

	// Assert
	assert.Equal(t, http.StatusInternalServerError, w.Code)
	var response map[string]string
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Contains(t, response["error"], "Failed to fetch comments")
	mockUC.AssertExpectations(t)
}

func TestVKHandler_TaskStatus_Success(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	expectedStatus := "completed"
	expectedComments := []comments.Comment{
		{ID: 1, Text: "Test comment 1"},
		{ID: 2, Text: "Test comment 2"},
	}
	mockUC.On("GetCommentsByTaskID", mock.Anything, "task-123").Return(expectedStatus, expectedComments, nil)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	c.Request = httptest.NewRequest("GET", "/api/vk/task/task-123", nil)
	c.Params = gin.Params{{Key: "task_id", Value: "task-123"}}

	// Act
	handler.TaskStatus(c)

	// Assert
	assert.Equal(t, http.StatusOK, w.Code)
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, expectedStatus, response["status"])
	assert.Len(t, response["comments"], 2)
	mockUC.AssertExpectations(t)
}

func TestVKHandler_TaskStatus_EmptyTaskID(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	c.Request = httptest.NewRequest("GET", "/api/vk/task/", nil)
	c.Params = gin.Params{{Key: "task_id", Value: ""}}

	// Act
	handler.TaskStatus(c)

	// Assert
	assert.Equal(t, http.StatusBadRequest, w.Code)
	var response map[string]string
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, "Task ID is required", response["error"])
	mockUC.AssertNotCalled(t, "GetCommentsByTaskID", mock.Anything, mock.Anything)
}

func TestVKHandler_TaskStatus_UseCaseError(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	expectedError := errors.New("use case error")
	mockUC.On("GetCommentsByTaskID", mock.Anything, "task-123").Return("", nil, expectedError)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	c.Request = httptest.NewRequest("GET", "/api/vk/task/task-123", nil)
	c.Params = gin.Params{{Key: "task_id", Value: "task-123"}}

	// Act
	handler.TaskStatus(c)

	// Assert
	assert.Equal(t, http.StatusInternalServerError, w.Code)
	var response map[string]string
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Contains(t, response["error"], "Failed to get task status")
	mockUC.AssertExpectations(t)
}

func TestVKHandler_ListComments_Success(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	expectedComments := []comments.Comment{
		{ID: 1, Text: "Test comment 1"},
		{ID: 2, Text: "Test comment 2"},
	}
	mockUC.On("ListComments", mock.Anything, "task-123", 10).Return(expectedComments, nil)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	c.Request = httptest.NewRequest("GET", "/api/comments?task_id=task-123&limit=10", nil)
	c.Request.URL.RawQuery = "task_id=task-123&limit=10"

	// Act
	handler.ListComments(c)

	// Assert
	assert.Equal(t, http.StatusOK, w.Code)
	var response []comments.Comment
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Len(t, response, 2)
	mockUC.AssertExpectations(t)
}

func TestVKHandler_ListComments_InvalidLimit(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	c.Request = httptest.NewRequest("GET", "/api/comments?limit=invalid", nil)
	c.Request.URL.RawQuery = "limit=invalid"

	// Act
	handler.ListComments(c)

	// Assert
	assert.Equal(t, http.StatusBadRequest, w.Code)
	var response map[string]string
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Contains(t, response["error"], "Invalid limit")
	mockUC.AssertNotCalled(t, "ListComments", mock.Anything, mock.Anything, mock.Anything)
}

func TestVKHandler_ListComments_NegativeLimit(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	expectedComments := []comments.Comment{
		{ID: 1, Text: "Test comment 1"},
	}
	mockUC.On("ListComments", mock.Anything, "", -5).Return(expectedComments, nil)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	c.Request = httptest.NewRequest("GET", "/api/comments?limit=-5", nil)
	c.Request.URL.RawQuery = "limit=-5"

	// Act
	handler.ListComments(c)

	// Assert
	assert.Equal(t, http.StatusOK, w.Code)
	var response []comments.Comment
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Len(t, response, 1)
	mockUC.AssertExpectations(t)
}

func TestVKHandler_ListComments_UseCaseError(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	expectedError := errors.New("use case error")
	mockUC.On("ListComments", mock.Anything, "task-123", 10).Return(nil, expectedError)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	c.Request = httptest.NewRequest("GET", "/api/comments?task_id=task-123&limit=10", nil)
	c.Request.URL.RawQuery = "task_id=task-123&limit=10"

	// Act
	handler.ListComments(c)

	// Assert
	assert.Equal(t, http.StatusInternalServerError, w.Code)
	var response map[string]string
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Contains(t, response["error"], "Failed to list comments")
	mockUC.AssertExpectations(t)
}

func TestVKHandler_ListComments_DefaultLimit(t *testing.T) {
	// Arrange
	mockUC := new(MockVKCommentsUseCase)
	handler := NewVKHandler(mockUC)
	
	expectedComments := []comments.Comment{
		{ID: 1, Text: "Test comment 1"},
	}
	mockUC.On("ListComments", mock.Anything, "", 10).Return(expectedComments, nil)
	
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	c.Request = httptest.NewRequest("GET", "/api/comments", nil)

	// Act
	handler.ListComments(c)

	// Assert
	assert.Equal(t, http.StatusOK, w.Code)
	var response []comments.Comment
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Len(t, response, 1)
	mockUC.AssertExpectations(t)
}
