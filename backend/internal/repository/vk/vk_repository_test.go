package vk

import (
	"context"
	"errors"
	"net/http"
	"testing"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"golang.org/x/time/rate"

	"vk-analyzer/internal/domain/vk"
)

// MockRestyClient - mock для resty.Client
type MockRestyClient struct {
	mock.Mock
}

func (m *MockRestyClient) R() *resty.Request {
	args := m.Called()
	return args.Get(0).(*resty.Request)
}

func (m *MockRestyClient) SetBaseURL(url string) {
	m.Called(url)
}

func (m *MockRestyClient) New() *resty.Client {
	args := m.Called()
	return args.Get(0).(*resty.Client)
}

// MockRestyRequest - mock для resty.Request
type MockRestyRequest struct {
	mock.Mock
}

func (m *MockRestyRequest) SetQueryParams(params map[string]string) *resty.Request {
	m.Called(params)
	return &resty.Request{}
}

func (m *MockRestyRequest) SetResult(result interface{}) *resty.Request {
	m.Called(result)
	return &resty.Request{}
}

func (m *MockRestyRequest) Get(url string) (*resty.Response, error) {
	args := m.Called(url)
	return args.Get(0).(*resty.Response), args.Error(1)
}

// MockRestyResponse - mock для resty.Response
type MockRestyResponse struct {
	mock.Mock
}

func (m *MockRestyResponse) IsSuccess() bool {
	args := m.Called()
	return args.Bool(0)
}

func (m *MockRestyResponse) IsError() bool {
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

// MockRateLimiter - mock для rate.Limiter
type MockRateLimiter struct {
	mock.Mock
}

func (m *MockRateLimiter) Wait(ctx context.Context) error {
	args := m.Called(ctx)
	return args.Error(0)
}

func TestNewVKRepository(t *testing.T) {
	// Тест создания нового репозитория
	repo := NewVKRepository()

	// Проверяем, что репозиторий создан и имеет правильный тип
	assert.NotNil(t, repo)
	assert.IsType(t, &vkRepository{}, repo)

	// Проверяем, что это VKRepository интерфейс
	var _ VKRepository = repo
}

func TestVKRepository_GetComments_Success(t *testing.T) {
	// Тест успешного получения комментариев
	mockLimiter := new(MockRateLimiter)
	mockClient := new(MockRestyClient)
	mockRequest := new(MockRestyRequest)
	mockResponse := new(MockRestyResponse)

	// Настраиваем моки
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient.On("R").Return(mockRequest)
	mockRequest.On("SetQueryParams", mock.Anything).Return(mockRequest)
	mockRequest.On("SetResult", mock.Anything).Return(mockRequest)
	mockRequest.On("Get", "method/wall.getComments").Return(mockResponse, nil)
	mockResponse.On("IsSuccess").Return(true)
	mockResponse.On("Result").Return(&vkResponse{
		Response: vkItemsResponse{
			Items: &[]vk.VKComment{
				{ID: 123, FromID: 456, Text: "Test comment"},
			},
		},
	})

	// Создаем репозиторий с моками
	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Выполняем запрос
	comments, err := repo.GetComments(context.Background(), -123, 456, "test_token")

	// Проверяем результаты
	assert.NoError(t, err)
	assert.Len(t, comments, 1)
	assert.Equal(t, int64(123), comments[0].ID)
	assert.Equal(t, int64(456), comments[0].FromID)
	assert.Equal(t, "Test comment", comments[0].Text)

	// Проверяем, что все методы были вызваны
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockRequest.AssertExpectations(t)
	mockResponse.AssertExpectations(t)
}

func TestVKRepository_GetComments_RateLimitError(t *testing.T) {
	// Тест ошибки rate limiting
	mockLimiter := new(MockRateLimiter)
	mockClient := new(MockRestyClient)

	// Настраиваем мок rate limiter на возврат ошибки
	mockLimiter.On("Wait", mock.Anything).Return(errors.New("rate limit exceeded"))

	// Создаем репозиторий с моками
	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Выполняем запрос
	comments, err := repo.GetComments(context.Background(), -123, 456, "test_token")

	// Проверяем результаты
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "rate limit wait")
	assert.Empty(t, comments)

	// Проверяем, что rate limiter был вызван
	mockLimiter.AssertExpectations(t)
}

func TestVKRepository_GetComments_HTTPError(t *testing.T) {
	// Тест HTTP ошибки
	mockLimiter := new(MockRateLimiter)
	mockClient := new(MockRestyClient)
	mockRequest := new(MockRestyRequest)
	mockResponse := new(MockRestyResponse)

	// Настраиваем моки
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient.On("R").Return(mockRequest)
	mockRequest.On("SetQueryParams", mock.Anything).Return(mockRequest)
	mockRequest.On("SetResult", mock.Anything).Return(mockRequest)
	mockRequest.On("Get", "method/wall.getComments").Return(mockResponse, nil)
	mockResponse.On("IsSuccess").Return(false)
	mockResponse.On("StatusCode").Return(500)
	mockResponse.On("String").Return("Internal Server Error")

	// Создаем репозиторий с моками
	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Выполняем запрос
	comments, err := repo.GetComments(context.Background(), -123, 456, "test_token")

	// Проверяем результаты
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "VK API error: 500")
	assert.Empty(t, comments)

	// Проверяем, что все методы были вызваны
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockRequest.AssertExpectations(t)
	mockResponse.AssertExpectations(t)
}

func TestVKRepository_GetComments_RateLimit429Retry(t *testing.T) {
	// Тест retry логики при rate limit (429)
	mockLimiter := new(MockRateLimiter)
	mockClient := new(MockRestyClient)
	mockRequest := new(MockRestyRequest)
	mockResponse := new(MockRestyResponse)

	// Настраиваем моки для сценария с retry
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient.On("R").Return(mockRequest)
	mockRequest.On("SetQueryParams", mock.Anything).Return(mockRequest)
	mockRequest.On("SetResult", mock.Anything).Return(mockRequest)
	
	// Первый вызов возвращает 429, второй - успешный ответ
	mockRequest.On("Get", "method/wall.getComments").Return(mockResponse, nil).Times(2)
	mockResponse.On("IsSuccess").Return(false).Once()
	mockResponse.On("IsSuccess").Return(true).Once()
	mockResponse.On("StatusCode").Return(429).Once()
	mockResponse.On("StatusCode").Return(200).Once()
	mockResponse.On("Result").Return(&vkResponse{
		Response: vkItemsResponse{
			Items: &[]vk.VKComment{
				{ID: 123, FromID: 456, Text: "Test comment"},
			},
		},
	}).Once()

	// Создаем репозиторий с моками
	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Выполняем запрос
	comments, err := repo.GetComments(context.Background(), -123, 456, "test_token")

	// Проверяем результаты
	assert.NoError(t, err)
	assert.Len(t, comments, 1)
	assert.Equal(t, int64(123), comments[0].ID)

	// Проверяем, что все методы были вызваны
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockRequest.AssertExpectations(t)
	mockResponse.AssertExpectations(t)
}

func TestVKRepository_GetComments_MaxRetriesExceeded(t *testing.T) {
	// Тест превышения максимального количества retry попыток
	mockLimiter := new(MockRateLimiter)
	mockClient := new(MockRestyClient)
	mockRequest := new(MockRestyRequest)
	mockResponse := new(MockRestyResponse)

	// Настраиваем моки для сценария с превышением лимита retry
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient.On("R").Return(mockRequest)
	mockRequest.On("SetQueryParams", mock.Anything).Return(mockRequest)
	mockRequest.On("SetResult", mock.Anything).Return(mockRequest)
	
	// Все вызовы возвращают 429 (rate limit)
	mockRequest.On("Get", "method/wall.getComments").Return(mockResponse, nil).Times(5)
	mockResponse.On("IsSuccess").Return(false).Times(5)
	mockResponse.On("StatusCode").Return(429).Times(5)

	// Создаем репозиторий с моками
	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Выполняем запрос
	comments, err := repo.GetComments(context.Background(), -123, 456, "test_token")

	// Проверяем результаты
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "max retries exceeded")
	assert.Empty(t, comments)

	// Проверяем, что все методы были вызваны
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockRequest.AssertExpectations(t)
	mockResponse.AssertExpectations(t)
}

func TestVKRepository_GetPosts_Success(t *testing.T) {
	// Тест успешного получения постов
	mockLimiter := new(MockRateLimiter)
	mockClient := new(MockRestyClient)
	mockRequest := new(MockRestyRequest)
	mockResponse := new(MockRestyResponse)

	// Настраиваем моки
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient.On("R").Return(mockRequest)
	mockRequest.On("SetQueryParams", mock.Anything).Return(mockRequest)
	mockRequest.On("SetResult", mock.Anything).Return(mockRequest)
	mockRequest.On("Get", "method/wall.get").Return(mockResponse, nil)
	mockResponse.On("IsSuccess").Return(true)
	mockResponse.On("Result").Return(&vkResponse{
		Response: vkItemsResponse{
			Items: &[]vk.VKPost{
				{ID: 123, OwnerID: 456, Text: "Test post"},
			},
		},
	})

	// Создаем репозиторий с моками
	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Выполняем запрос
	posts, err := repo.GetPosts(context.Background(), -123, 10, 0, "test_token")

	// Проверяем результаты
	assert.NoError(t, err)
	assert.Len(t, posts, 1)
	assert.Equal(t, int64(123), posts[0].ID)
	assert.Equal(t, int64(456), posts[0].OwnerID)
	assert.Equal(t, "Test post", posts[0].Text)

	// Проверяем, что все методы были вызваны
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockRequest.AssertExpectations(t)
	mockResponse.AssertExpectations(t)
}

func TestVKRepository_GetLikesList_Success(t *testing.T) {
	// Тест успешного получения списка лайков
	mockLimiter := new(MockRateLimiter)
	mockClient := new(MockRestyClient)
	mockRequest := new(MockRestyRequest)
	mockResponse := new(MockRestyResponse)

	// Настраиваем моки
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient.On("R").Return(mockRequest)
	mockRequest.On("SetQueryParams", mock.Anything).Return(mockRequest)
	mockRequest.On("SetResult", mock.Anything).Return(mockRequest)
	mockRequest.On("Get", "method/likes.getList").Return(mockResponse, nil)
	mockResponse.On("IsSuccess").Return(true)
	mockResponse.On("Result").Return(&vkResponse{
		Response: vkItemsResponse{
			Items: &[]int64{123, 456, 789},
		},
	})

	// Создаем репозиторий с моками
	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Выполняем запрос
	userIDs, err := repo.GetLikesList(context.Background(), "post", -123, 456, "test_token")

	// Проверяем результаты
	assert.NoError(t, err)
	assert.Len(t, userIDs, 3)
	assert.Equal(t, []int64{123, 456, 789}, userIDs)

	// Проверяем, что все методы были вызваны
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockRequest.AssertExpectations(t)
	mockResponse.AssertExpectations(t)
}

func TestVKRepository_ConcurrentRequests(t *testing.T) {
	// Тест параллельных запросов с rate limiting
	mockLimiter := new(MockRateLimiter)
	mockClient := new(MockRestyClient)
	mockRequest := new(MockRestyRequest)
	mockResponse := new(MockRestyResponse)

	// Настраиваем моки для параллельных вызовов
	mockLimiter.On("Wait", mock.Anything).Return(nil).Times(3)
	mockClient.On("R").Return(mockRequest).Times(3)
	mockRequest.On("SetQueryParams", mock.Anything).Return(mockRequest).Times(3)
	mockRequest.On("SetResult", mock.Anything).Return(mockRequest).Times(3)
	mockRequest.On("Get", mock.Anything).Return(mockResponse, nil).Times(3)
	mockResponse.On("IsSuccess").Return(true).Times(3)
	mockResponse.On("Result").Return(&vkResponse{
		Response: vkItemsResponse{
			Items: &[]vk.VKComment{
				{ID: 123, FromID: 456, Text: "Test comment"},
			},
		},
	}).Times(3)

	// Создаем репозиторий с моками
	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Выполняем параллельные запросы
	ctx := context.Background()
	ownerID := int64(-123)
	postID := int64(456)
	token := "test_token"

	// Запускаем 3 параллельных запроса
	done := make(chan struct{}, 3)
	for i := 0; i < 3; i++ {
		go func() {
			_, err := repo.GetComments(ctx, ownerID, postID, token)
			assert.NoError(t, err)
			done <- struct{}{}
		}()
	}

	// Ждем завершения всех запросов
	for i := 0; i < 3; i++ {
		<-done
	}

	// Проверяем, что все методы были вызваны правильное количество раз
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockRequest.AssertExpectations(t)
	mockResponse.AssertExpectations(t)
}

func TestVKRepository_ExecuteWithRetry_ContextTimeout(t *testing.T) {
	// Тест таймаута контекста в retry логике
	mockLimiter := new(MockRateLimiter)
	mockClient := new(MockRestyClient)
	mockRequest := new(MockRestyRequest)
	mockResponse := new(MockRestyResponse)

	// Создаем контекст с таймаутом
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()

	// Настраиваем моки
	mockLimiter.On("Wait", mock.Anything).Return(nil)
	mockClient.On("R").Return(mockRequest)
	mockRequest.On("SetQueryParams", mock.Anything).Return(mockRequest)
	mockRequest.On("SetResult", mock.Anything).Return(mockRequest)
	
	// Настраиваем ответы с задержкой больше таймаута
	mockRequest.On("Get", "method/wall.getComments").Return(mockResponse, nil).Times(5)
	mockResponse.On("IsSuccess").Return(false).Times(5)
	mockResponse.On("StatusCode").Return(429).Times(5)

	// Создаем репозиторий с моками
	repo := &vkRepository{
		client:  mockClient,
		limiter: mockLimiter,
	}

	// Выполняем запрос
	comments, err := repo.GetComments(ctx, -123, 456, "test_token")

	// Проверяем результаты
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "context deadline exceeded")
	assert.Empty(t, comments)

	// Проверяем, что методы были вызваны
	mockLimiter.AssertExpectations(t)
	mockClient.AssertExpectations(t)
	mockRequest.AssertExpectations(t)
	mockResponse.AssertExpectations(t)
}
