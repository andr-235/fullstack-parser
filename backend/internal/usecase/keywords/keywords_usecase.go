// Package keywords содержит use cases для модуля ключевых слов.
// Use cases координируют domain и infrastructure слои.

package keywords

import (
	"context"

	"backend/internal/domain/keywords"
	"backend/internal/repository/postgres"

	"github.com/sirupsen/logrus"
)

// UseCase - интерфейс для use cases ключевых слов.
type UseCase interface {
	CreateKeyword(ctx context.Context, text, description string) (*keywords.Keyword, error)
	GetKeyword(ctx context.Context, id uint) (*keywords.Keyword, error)
	UpdateKeyword(ctx context.Context, id uint, text, description string) (*keywords.Keyword, error)
	DeleteKeyword(ctx context.Context, id uint) error
	ActivateKeyword(ctx context.Context, id uint) error
	DeactivateKeyword(ctx context.Context, id uint) error
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
