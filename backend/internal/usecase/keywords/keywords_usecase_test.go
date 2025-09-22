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

	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockKeywordRepository - mock для KeywordRepository.
type MockKeywordRepository struct {
	mock.Mock
}

// Create mock.
func (m *MockKeywordRepository) Create(ctx context.Context, k *keywords.Keyword) error {
	args := m.Called(ctx, k)
	return args.Error(0)
}

// GetByID mock.
func (m *MockKeywordRepository) GetByID(ctx context.Context, id uint) (*keywords.Keyword, error) {
	args := m.Called(ctx, id)
	return args.Get(0).(*keywords.Keyword), args.Error(1)
}

// Update mock.
func (m *MockKeywordRepository) Update(ctx context.Context, k *keywords.Keyword) error {
	args := m.Called(ctx, k)
	return args.Error(0)
}

// Delete mock.
func (m *MockKeywordRepository) Delete(ctx context.Context, id uint) error {
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
	logger := logrus.New()
	service := keywords.NewKeywordService()
	repo := new(MockKeywordRepository)
	uc := NewUseCase(repo, service, logger)

	text := "test"
	description := "test desc"
	k := &keywords.Keyword{
		Text:        text,
		Description: description,
		Active:      true,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	repo.On("Create", mock.Anything, mock.AnythingOfType("*keywords.Keyword")).Return(nil)

	result, err := uc.CreateKeyword(context.Background(), text, description)

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, text, result.Text)
	repo.AssertExpectations(t)
}

// TestCreateKeyword_InvalidText тестирует валидацию.
func TestCreateKeyword_InvalidText(t *testing.T) {
	logger := logrus.New()
	service := keywords.NewKeywordService()
	repo := new(MockKeywordRepository)
	uc := NewUseCase(repo, service, logger)

	_, err := uc.CreateKeyword(context.Background(), "", "")

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "текст не может быть пустым")
}

// TestGetKeyword тестирует получение по ID.
func TestGetKeyword(t *testing.T) {
	logger := logrus.New()
	service := keywords.NewKeywordService()
	repo := new(MockKeywordRepository)
	uc := NewUseCase(repo, service, logger)

	id := uint(1)
	k := &keywords.Keyword{ID: id, Text: "test"}

	repo.On("GetByID", mock.Anything, id).Return(k, nil)

	result, err := uc.GetKeyword(context.Background(), id)

	assert.NoError(t, err)
	assert.Equal(t, k, result)
	repo.AssertExpectations(t)
}

// TestUpdateKeyword тестирует обновление.
func TestUpdateKeyword(t *testing.T) {
	logger := logrus.New()
	service := keywords.NewKeywordService()
	repo := new(MockKeywordRepository)
	uc := NewUseCase(repo, service, logger)

	id := uint(1)
	text := "updated"
	description := "updated desc"
	k := &keywords.Keyword{ID: id, Text: "old"}

	repo.On("GetByID", mock.Anything, id).Return(k, nil)
	repo.On("Update", mock.Anything, mock.AnythingOfType("*keywords.Keyword")).Return(nil)

	result, err := uc.UpdateKeyword(context.Background(), id, text, description)

	assert.NoError(t, err)
	assert.Equal(t, text, result.Text)
	repo.AssertExpectations(t)
}

// TestDeleteKeyword тестирует удаление.
func TestDeleteKeyword(t *testing.T) {
	logger := logrus.New()
	service := keywords.NewKeywordService()
	repo := new(MockKeywordRepository)
	uc := NewUseCase(repo, service, logger)

	id := uint(1)

	repo.On("Delete", mock.Anything, id).Return(nil)

	err := uc.DeleteKeyword(context.Background(), id)

	assert.NoError(t, err)
	repo.AssertExpectations(t)
}

// TestActivateKeyword тестирует активацию.
func TestActivateKeyword(t *testing.T) {
	logger := logrus.New()
	service := keywords.NewKeywordService()
	repo := new(MockKeywordRepository)
	uc := NewUseCase(repo, service, logger)

	id := uint(1)
	k := &keywords.Keyword{ID: id, Active: false}

	repo.On("GetByID", mock.Anything, id).Return(k, nil)
	repo.On("Update", mock.Anything, mock.AnythingOfType("*keywords.Keyword")).Return(nil)

	err := uc.ActivateKeyword(context.Background(), id)

	assert.NoError(t, err)
	assert.True(t, k.Active)
	repo.AssertExpectations(t)
}

// TestDeactivateKeyword тестирует деактивацию.
func TestDeactivateKeyword(t *testing.T) {
	logger := logrus.New()
	service := keywords.NewKeywordService()
	repo := new(MockKeywordRepository)
	uc := NewUseCase(repo, service, logger)

	id := uint(1)
	k := &keywords.Keyword{ID: id, Active: true}

	repo.On("GetByID", mock.Anything, id).Return(k, nil)
	repo.On("Update", mock.Anything, mock.AnythingOfType("*keywords.Keyword")).Return(nil)

	err := uc.DeactivateKeyword(context.Background(), id)

	assert.NoError(t, err)
	assert.False(t, k.Active)
	repo.AssertExpectations(t)
}

// TestListKeywords тестирует список.
func TestListKeywords(t *testing.T) {
	logger := logrus.New()
	service := keywords.NewKeywordService()
	repo := new(MockKeywordRepository)
	uc := NewUseCase(repo, service, logger)

	activeOnly := true
	list := []*keywords.Keyword{{ID: 1, Text: "test", Active: true}}

	repo.On("List", mock.Anything, activeOnly).Return(list, nil)

	result, err := uc.ListKeywords(context.Background(), activeOnly)

	assert.NoError(t, err)
	assert.Equal(t, list, result)
	repo.AssertExpectations(t)
}

// TestGetKeywordStats тестирует статистику.
func TestGetKeywordStats(t *testing.T) {
	logger := logrus.New()
	service := keywords.NewKeywordService()
	repo := new(MockKeywordRepository)
	uc := NewUseCase(repo, service, logger)

	stats := &postgres.KeywordStats{Total: 1, Active: 1, Usage: 0}

	repo.On("GetStats", mock.Anything).Return(stats, nil)

	result, err := uc.GetKeywordStats(context.Background())

	assert.NoError(t, err)
	assert.Equal(t, stats, result)
	repo.AssertExpectations(t)
}