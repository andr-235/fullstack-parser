// Package keywords содержит unit-тесты для use cases ключевых слов.
// Тесты используют testify для assertions и mocks.

package keywords

import (
	"context"
	"errors"
	"testing"
	"time"

	"backend/internal/domain/keywords"
	"backend/internal/repository/postgres"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockKeywordRepository - mock для KeywordRepository.
type MockKeywordRepository struct {
	mock.Mock
}

// Вспомогательные функции для тестов
func createTestKeyword(id uuid.UUID, text string, active bool) *keywords.Keyword {
	return &keywords.Keyword{
		ID:          id,
		Text:        text,
		Description: "test description",
		Active:      active,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
}

func createTestUseCase() (UseCase, *MockKeywordRepository) {
	logger := logrus.New()
	service := keywords.NewKeywordService()
	repo := new(MockKeywordRepository)
	uc := NewUseCase(repo, service, logger)
	return uc, repo
}

// Create mock.
func (m *MockKeywordRepository) Create(ctx context.Context, k *keywords.Keyword) error {
	args := m.Called(ctx, k)
	return args.Error(0)
}

// GetByID mock.
func (m *MockKeywordRepository) GetByID(ctx context.Context, id uuid.UUID) (*keywords.Keyword, error) {
	args := m.Called(ctx, id)
	return args.Get(0).(*keywords.Keyword), args.Error(1)
}

// Update mock.
func (m *MockKeywordRepository) Update(ctx context.Context, k *keywords.Keyword) error {
	args := m.Called(ctx, k)
	return args.Error(0)
}

// Delete mock.
func (m *MockKeywordRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// List mock.
func (m *MockKeywordRepository) List(ctx context.Context, activeOnly bool) ([]*keywords.Keyword, error) {
	args := m.Called(ctx, activeOnly)
	return args.Get(0).([]*keywords.Keyword), args.Error(1)
}

// GetStats mock.
func (m *MockKeywordRepository) GetStats(ctx context.Context) (*postgres.KeywordStats, error) {
	args := m.Called(ctx)
	return args.Get(0).(*postgres.KeywordStats), args.Error(1)
}

// TestCreateKeyword тестирует создание ключевого слова.
func TestCreateKeyword(t *testing.T) {
	uc, repo := createTestUseCase()

	text := "test"
	description := "test desc"

	repo.On("Create", mock.Anything, mock.AnythingOfType("*keywords.Keyword")).Return(nil)

	result, err := uc.CreateKeyword(context.Background(), text, description)

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, text, result.Text)
	assert.Equal(t, description, result.Description)
	assert.True(t, result.Active)
	repo.AssertExpectations(t)
}

// TestCreateKeyword_InvalidText тестирует валидацию.
func TestCreateKeyword_InvalidText(t *testing.T) {
	uc, _ := createTestUseCase()

	_, err := uc.CreateKeyword(context.Background(), "", "")

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "текст не может быть пустым")
}

// TestGetKeyword тестирует получение по ID.
func TestGetKeyword(t *testing.T) {
	uc, repo := createTestUseCase()

	id := uuid.New()
	k := createTestKeyword(id, "test", true)

	repo.On("GetByID", mock.Anything, id).Return(k, nil)

	result, err := uc.GetKeyword(context.Background(), id)

	assert.NoError(t, err)
	assert.Equal(t, k, result)
	repo.AssertExpectations(t)
}

// TestUpdateKeyword тестирует обновление.
func TestUpdateKeyword(t *testing.T) {
	uc, repo := createTestUseCase()

	id := uuid.New()
	text := "updated"
	description := "updated desc"
	k := createTestKeyword(id, "old", true)

	repo.On("GetByID", mock.Anything, id).Return(k, nil)
	repo.On("Update", mock.Anything, mock.AnythingOfType("*keywords.Keyword")).Return(nil)

	result, err := uc.UpdateKeyword(context.Background(), id, text, description)

	assert.NoError(t, err)
	assert.Equal(t, text, result.Text)
	assert.Equal(t, description, result.Description)
	repo.AssertExpectations(t)
}

// TestDeleteKeyword тестирует удаление.
func TestDeleteKeyword(t *testing.T) {
	uc, repo := createTestUseCase()

	id := uuid.New()

	repo.On("Delete", mock.Anything, id).Return(nil)

	err := uc.DeleteKeyword(context.Background(), id)

	assert.NoError(t, err)
	repo.AssertExpectations(t)
}

// TestActivateKeyword тестирует активацию.
func TestActivateKeyword(t *testing.T) {
	uc, repo := createTestUseCase()

	id := uuid.New()
	k := createTestKeyword(id, "test", false)

	repo.On("GetByID", mock.Anything, id).Return(k, nil)
	repo.On("Update", mock.Anything, mock.AnythingOfType("*keywords.Keyword")).Return(nil)

	err := uc.ActivateKeyword(context.Background(), id)

	assert.NoError(t, err)
	assert.True(t, k.Active)
	repo.AssertExpectations(t)
}

// TestDeactivateKeyword тестирует деактивацию.
func TestDeactivateKeyword(t *testing.T) {
	uc, repo := createTestUseCase()

	id := uuid.New()
	k := createTestKeyword(id, "test", true)

	repo.On("GetByID", mock.Anything, id).Return(k, nil)
	repo.On("Update", mock.Anything, mock.AnythingOfType("*keywords.Keyword")).Return(nil)

	err := uc.DeactivateKeyword(context.Background(), id)

	assert.NoError(t, err)
	assert.False(t, k.Active)
	repo.AssertExpectations(t)
}

// TestListKeywords тестирует список.
func TestListKeywords(t *testing.T) {
	uc, repo := createTestUseCase()

	activeOnly := true
	id := uuid.New()
	list := []*keywords.Keyword{createTestKeyword(id, "test", true)}

	repo.On("List", mock.Anything, activeOnly).Return(list, nil)

	result, err := uc.ListKeywords(context.Background(), activeOnly)

	assert.NoError(t, err)
	assert.Equal(t, list, result)
	repo.AssertExpectations(t)
}

// TestGetKeywordStats тестирует статистику.
func TestGetKeywordStats(t *testing.T) {
	uc, repo := createTestUseCase()

	stats := &postgres.KeywordStats{Total: 1, Active: 1, Usage: 0}

	repo.On("GetStats", mock.Anything).Return(stats, nil)

	result, err := uc.GetKeywordStats(context.Background())

	assert.NoError(t, err)
	assert.Equal(t, stats, result)
	repo.AssertExpectations(t)
}

// TestGetKeyword_NotFound тестирует случай, когда ключевое слово не найдено.
func TestGetKeyword_NotFound(t *testing.T) {
	uc, repo := createTestUseCase()

	id := uuid.New()
	repo.On("GetByID", mock.Anything, id).Return((*keywords.Keyword)(nil), errors.New("ключ не найден"))

	result, err := uc.GetKeyword(context.Background(), id)

	assert.Error(t, err)
	assert.Nil(t, result)
	repo.AssertExpectations(t)
}

// TestUpdateKeyword_NotFound тестирует обновление несуществующего ключевого слова.
func TestUpdateKeyword_NotFound(t *testing.T) {
	uc, repo := createTestUseCase()

	id := uuid.New()
	text := "updated"
	description := "updated desc"

	repo.On("GetByID", mock.Anything, id).Return((*keywords.Keyword)(nil), errors.New("ключ не найден"))

	result, err := uc.UpdateKeyword(context.Background(), id, text, description)

	assert.Error(t, err)
	assert.Nil(t, result)
	repo.AssertExpectations(t)
}

// TestActivateKeyword_NotFound тестирует активацию несуществующего ключевого слова.
func TestActivateKeyword_NotFound(t *testing.T) {
	uc, repo := createTestUseCase()

	id := uuid.New()
	repo.On("GetByID", mock.Anything, id).Return((*keywords.Keyword)(nil), errors.New("ключ не найден"))

	err := uc.ActivateKeyword(context.Background(), id)

	assert.Error(t, err)
	repo.AssertExpectations(t)
}
