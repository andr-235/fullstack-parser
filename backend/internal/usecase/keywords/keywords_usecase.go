// Package keywords содержит use cases для модуля ключевых слов.
// Use cases координируют domain и infrastructure слои.

package keywords

import (
	"context"

	"backend/internal/domain/keywords"
	"backend/internal/repository/postgres"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

// UseCase - интерфейс для use cases ключевых слов.
type UseCase interface {
	CreateKeyword(ctx context.Context, text, description string) (*keywords.Keyword, error)
	GetKeyword(ctx context.Context, id uuid.UUID) (*keywords.Keyword, error)
	UpdateKeyword(ctx context.Context, id uuid.UUID, text, description string) (*keywords.Keyword, error)
	DeleteKeyword(ctx context.Context, id uuid.UUID) error
	ActivateKeyword(ctx context.Context, id uuid.UUID) error
	DeactivateKeyword(ctx context.Context, id uuid.UUID) error
	ListKeywords(ctx context.Context, activeOnly bool) ([]*keywords.Keyword, error)
	GetKeywordStats(ctx context.Context) (*postgres.KeywordStats, error)
}

// keywordUseCase - реализация UseCase.
type keywordUseCase struct {
	repo    postgres.KeywordRepository
	service *keywords.KeywordService
	logger  *logrus.Logger
}

// NewUseCase создает новый экземпляр keywordUseCase.
func NewUseCase(repo postgres.KeywordRepository, service *keywords.KeywordService, logger *logrus.Logger) UseCase {
	return &keywordUseCase{
		repo:    repo,
		service: service,
		logger:  logger,
	}
}

// CreateKeyword создает новое ключевое слово.
func (uc *keywordUseCase) CreateKeyword(ctx context.Context, text, description string) (*keywords.Keyword, error) {
	// Placeholder: проверка роли admin из JWT.
	uc.logger.WithField("text", text).Info("создание ключевого слова")

	if err := uc.service.ValidateKeywordText(text); err != nil {
		uc.logger.WithError(err).Error("валидация текста провалена")
		return nil, err
	}

	k, err := keywords.NewKeyword(text, description)
	if err != nil {
		uc.logger.WithError(err).Error("ошибка создания доменной сущности")
		return nil, err
	}

	if err := uc.repo.Create(ctx, k); err != nil {
		uc.logger.WithError(err).Error("ошибка сохранения в репозиторий")
		return nil, err
	}

	uc.logger.WithField("id", k.ID).Info("ключ создано успешно")
	return k, nil
}

// GetKeyword получает ключевое слово по ID.
func (uc *keywordUseCase) GetKeyword(ctx context.Context, id uuid.UUID) (*keywords.Keyword, error) {
	return uc.repo.GetByID(ctx, id)
}

// UpdateKeyword обновляет ключевое слово.
func (uc *keywordUseCase) UpdateKeyword(ctx context.Context, id uuid.UUID, text, description string) (*keywords.Keyword, error) {
	keyword, err := uc.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}

	keyword.Text = text
	keyword.Description = description

	return keyword, uc.repo.Update(ctx, keyword)
}

// DeleteKeyword удаляет ключевое слово.
func (uc *keywordUseCase) DeleteKeyword(ctx context.Context, id uuid.UUID) error {
	return uc.repo.Delete(ctx, id)
}

// ActivateKeyword активирует ключевое слово.
func (uc *keywordUseCase) ActivateKeyword(ctx context.Context, id uuid.UUID) error {
	keyword, err := uc.repo.GetByID(ctx, id)
	if err != nil {
		return err
	}

	keyword.Activate()
	return uc.repo.Update(ctx, keyword)
}

// DeactivateKeyword деактивирует ключевое слово.
func (uc *keywordUseCase) DeactivateKeyword(ctx context.Context, id uuid.UUID) error {
	keyword, err := uc.repo.GetByID(ctx, id)
	if err != nil {
		return err
	}

	keyword.Deactivate()
	return uc.repo.Update(ctx, keyword)
}

// ListKeywords получает список ключевых слов.
func (uc *keywordUseCase) ListKeywords(ctx context.Context, activeOnly bool) ([]*keywords.Keyword, error) {
	return uc.repo.List(ctx, activeOnly)
}

// GetKeywordStats получает статистику по ключевым словам.
func (uc *keywordUseCase) GetKeywordStats(ctx context.Context) (*postgres.KeywordStats, error) {
	return uc.repo.GetStats(ctx)
}
