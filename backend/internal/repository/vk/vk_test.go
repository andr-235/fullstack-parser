package vk

import (
	"context"
	"errors"
	"testing"
	"time"

	"vk-analyzer/internal/domain/vk"

	"github.com/go-resty/resty/v2"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockRestyClient struct {
	mock.Mock
}

func (m *MockRestyClient) R() *resty.Request {
	args := m.Called()
	return args.Get(0).(*resty.Request)
}

type MockRestyRequest struct {
	mock.Mock
}

func (m *MockRestyRequest) SetQueryParams(params map[string]string) *resty.Request {
	args := m.Called(params)
	return args.Get(0).(*resty.Request)
}

func (m *MockRestyRequest) SetResult(result interface{}) *resty.Request {
	args := m.Called(result)
	return args.Get(0).(*resty.Request)
}

func (m *MockRestyRequest) Get(url string) (*resty.Response, error) {
	args := m.Called(url)
	return args.Get(0).(*resty.Response), args.Error(1)
}

type MockRestyResponse struct {
	mock.Mock
}

func (m *MockRestyResponse) IsSuccess() bool {
	args := m.Called()
	return args.Bool(0)
}

func (m *MockRestyResponse) StatusCode() int {
	args := m.Called()
	return args.Int(0)
}

func (m *MockRestyResponse) String() string {
	args := m.Called()
	return args.String(0)
}

func (m *MockRestyResponse) Result() interface{} {
	args := m.Called()
	return args.Get(0)
}

type MockRateLimiter struct {
	mock.Mock
}

func (m *MockRateLimiter) Wait(ctx context.Context) error {
	args := m.Called(ctx)
	return args.Error(0)
}

func TestNewVKRepository(t *testing.T) {
	// Act
	repo := NewVKRepository()

	// Assert
	assert.NotNil(t, repo)
	assert.NotNil(t, repo.(*vkRepository).client)
	assert.NotNil(t, repo.(*vkRepository).limiter)
	assert.Equal(t, 3, repo.(*vkRepository).limiter.Limit())
	assert.Equal(t, 10, repo.(*vkRepository).limiter.Burst())
}

func TestGetComments_Success(t *testing.T) {
	// Arrange
	mockLimiter := &MockRateLimiter{}
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient := &MockRestyClient{}
	mockReq := &MockRestyRequest{}
	mockClient.On("R").Return(mockReq)
	mockReq.On("SetQueryParams", mock.Anything).Return(mockReq)
	mockReq.On("SetResult", mock.Anything).Return(mockReq)
	mockResp := &MockRestyResponse{}
	mockReq.On("Get", "method/wall.getComments").Return(mockResp, nil)
	mockResp.On("IsSuccess").Return(true)
	mockResp.On("StatusCode").Return(200)
	mockResp.On("String").Return("")
	result := &vkResponse{Response: vkItemsResponse{Items: &[]vk.VKComment{}}}
	mockResp.On("Result").Return(result)

	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Act
	comments, err := repo.GetComments(context.Background(), -123, 456, "test_token")

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, comments)
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockReq.AssertExpectations(t)
	mockResp.AssertExpectations(t)
}

func TestGetComments_RateLimitWaitError(t *testing.T) {
	// Arrange
	mockLimiter := &MockRateLimiter{}
	mockLimiter.On("Wait", mock.Anything).Return(errors.New("rate limit exceeded"))
	repo := &vkRepository{limiter: mockLimiter}

	// Act
	comments, err := repo.GetComments(context.Background(), -123, 456, "test_token")

	// Assert
	assert.Error(t, err)
	assert.Nil(t, comments)
	assert.Contains(t, err.Error(), "rate limit wait")
	mockLimiter.AssertExpectations(t)
}

func TestGetComments_HTTPError(t *testing.T) {
	// Arrange
	mockLimiter := &MockRateLimiter{}
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient := &MockRestyClient{}
	mockReq := &MockRestyRequest{}
	mockClient.On("R").Return(mockReq)
	mockReq.On("SetQueryParams", mock.Anything).Return(mockReq)
	mockReq.On("SetResult", mock.Anything).Return(mockReq)
	mockResp := &MockRestyResponse{}
	mockReq.On("Get", "method/wall.getComments").Return(mockResp, nil)
	mockResp.On("IsSuccess").Return(false)
	mockResp.On("StatusCode").Return(500)
	mockResp.On("String").Return("Server error")

	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Act
	comments, err := repo.GetComments(context.Background(), -123, 456, "test_token")

	// Assert
	assert.Error(t, err)
	assert.Nil(t, comments)
	assert.Contains(t, err.Error(), "VK API error: 500")
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockReq.AssertExpectations(t)
	mockResp.AssertExpectations(t)
}

func TestGetComments_RetryOn429_SuccessAfterRetry(t *testing.T) {
	// Arrange
	mockLimiter := &MockRateLimiter{}
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient := &MockRestyClient{}
	mockReq := &MockRestyRequest{}
	mockClient.On("R").Return(mockReq)
	mockReq.On("SetQueryParams", mock.Anything).Return(mockReq)
	mockReq.On("SetResult", mock.Anything).Return(mockReq)

	// First call returns 429
	mockResp1 := &MockRestyResponse{}
	mockReq.On("Get", "method/wall.getComments").Return(mockResp1, nil).Once()
	mockResp1.On("IsSuccess").Return(false)
	mockResp1.On("StatusCode").Return(429)
	mockResp1.On("String").Return("Rate limited")

	// Second call succeeds
	mockResp2 := &MockRestyResponse{}
	mockReq.On("Get", "method/wall.getComments").Return(mockResp2, nil).Once()
	mockResp2.On("IsSuccess").Return(true)
	mockResp2.On("StatusCode").Return(200)
	mockResp2.On("String").Return("")
	result := &vkResponse{Response: vkItemsResponse{Items: &[]vk.VKComment{}}}
	mockResp2.On("Result").Return(result)

	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Act
	comments, err := repo.GetComments(ctx, -123, 456, "test_token")

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, comments)
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockReq.AssertExpectations(t)
	mockResp1.AssertExpectations(t)
	mockResp2.AssertExpectations(t)
}

func TestGetComments_MaxRetriesExceeded(t *testing.T) {
	// Arrange
	mockLimiter := &MockRateLimiter{}
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient := &MockRestyClient{}
	mockReq := &MockRestyRequest{}
	mockClient.On("R").Return(mockReq)
	mockReq.On("SetQueryParams", mock.Anything).Return(mockReq)
	mockReq.On("SetResult", mock.Anything).Return(mockReq)
	mockResp := &MockRestyResponse{}
	mockReq.On("Get", "method/wall.getComments").Return(mockResp, nil).Times(5)
	mockResp.On("IsSuccess").Return(false)
	mockResp.On("StatusCode").Return(429)
	mockResp.On("String").Return("Rate limited")

	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	// Act
	comments, err := repo.GetComments(ctx, -123, 456, "test_token")

	// Assert
	assert.Error(t, err)
	assert.Nil(t, comments)
	assert.Contains(t, err.Error(), "max retries exceeded")
	mockLimiter.AssertNumberOfCalls(t, "Wait", 5)
	mockClient.AssertExpectations(t)
	mockReq.AssertExpectations(t)
	mockResp.AssertExpectations(t)
}

func TestExecuteWithRetry_SuccessOnFirstTry(t *testing.T) {
	// Arrange
	mockResp := &MockRestyResponse{}
	mockResp.On("IsSuccess").Return(true)

	fn := func() (*resty.Response, error) {
		return mockResp, nil
	}

	repo := &vkRepository{}

	// Act
	err := repo.executeWithRetry(context.Background(), fn)

	// Assert
	assert.NoError(t, err)
	mockResp.AssertExpectations(t)
}

func TestExecuteWithRetry_RetryOn429(t *testing.T) {
	// Arrange
	callCount := 0
	fn := func() (*resty.Response, error) {
		callCount++
		if callCount == 1 {
			return &MockRestyResponse{StatusCode: 429}, nil
		}
		return &MockRestyResponse{IsSuccess: true}, nil
	}

	repo := &vkRepository{}

	// Act
	err := repo.executeWithRetry(context.Background(), fn)

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, 2, callCount)
}
