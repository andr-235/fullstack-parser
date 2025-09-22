// Package postgres содержит реализации репозиториев для PostgreSQL с использованием GORM.

package postgres

import (
	"context"
	"errors"

	"gorm.io/gorm"

	"backend/internal/domain/keywords"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

// KeywordRepository - интерфейс для репозитория ключевых слов.
type KeywordRepository interface {
	Create(ctx context.Context, k *keywords.Keyword) error
	GetByID(ctx context.Context, id uuid.UUID) (*keywords.Keyword, error)
	Update(ctx context.Context, k *keywords.Keyword) error
	Delete(ctx context.Context, id uuid.UUID) error
	List(ctx context.Context, activeOnly bool) ([]*keywords.Keyword, error)
	GetStats(ctx context.Context) (*KeywordStats, error)
}

// keywordRepository - реализация KeywordRepository с GORM.
type keywordRepository struct {
	db *gorm.DB
}

// NewKeywordRepository создает новый экземпляр keywordRepository.
func NewKeywordRepository(db *gorm.DB) KeywordRepository {
	return &keywordRepository{db: db}
}

// KeywordStats представляет статистику ключевых слов.
type KeywordStats struct {
	Total  int `json:"total"`
	Active int `json:"active"`
	Usage  int `json:"usage"` // Placeholder для использования в комментариях.
}

// Create создает новое ключевое слово в БД.
func (r *keywordRepository) Create(ctx context.Context, k *keywords.Keyword) error {
	if err := r.db.WithContext(ctx).Create(k).Error; err != nil {
		logrus.WithError(err).WithField("text", k.Text).Error("ошибка создания ключевого слова")
		return err
	}
	return nil
}

// GetByID получает ключевое слово по ID.
func (r *keywordRepository) GetByID(ctx context.Context, id uuid.UUID) (*keywords.Keyword, error) {
	var k keywords.Keyword
	if err := r.db.WithContext(ctx).First(&k, "id = ?", id).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("ключ не найден")
		}
		logrus.WithError(err).WithField("id", id).Error("ошибка получения ключевого слова")
		return nil, err
	}
	return &k, nil
}

// Update обновляет ключевое слово в БД.
func (r *keywordRepository) Update(ctx context.Context, k *keywords.Keyword) error {
	if err := r.db.WithContext(ctx).Save(k).Error; err != nil {
		logrus.WithError(err).WithField("id", k.ID).Error("ошибка обновления ключевого слова")
		return err
	}
	return nil
}

// Delete удаляет ключевое слово по ID.
func (r *keywordRepository) Delete(ctx context.Context, id uuid.UUID) error {
	if err := r.db.WithContext(ctx).Delete(&keywords.Keyword{}, "id = ?", id).Error; err != nil {
		logrus.WithError(err).WithField("id", id).Error("ошибка удаления ключевого слова")
		return err
	}
	return nil
}

// List возвращает список ключевых слов, опционально только активные.
func (r *keywordRepository) List(ctx context.Context, activeOnly bool) ([]*keywords.Keyword, error) {
	var keywordsList []*keywords.Keyword
	query := r.db.WithContext(ctx).Model(&keywords.Keyword{})
	if activeOnly {
		query = query.Where("active = ?", true)
	}
	if err := query.Find(&keywordsList).Error; err != nil {
		logrus.WithError(err).Error("ошибка получения списка ключевых слов")
		return nil, err
	}
	return keywordsList, nil
}

// GetStats возвращает статистику ключевых слов.
// Usage - placeholder, в будущем интегрировать с comments repo для подсчета совпадений.
func (r *keywordRepository) GetStats(ctx context.Context) (*KeywordStats, error) {
	var total, active int64
	if err := r.db.WithContext(ctx).Model(&keywords.Keyword{}).Count(&total).Error; err != nil {
		logrus.WithError(err).Error("ошибка подсчета общего количества ключевых слов")
		return nil, err
	}
	if err := r.db.WithContext(ctx).Model(&keywords.Keyword{}).Where("active = ?", true).Count(&active).Error; err != nil {
		logrus.WithError(err).Error("ошибка подсчета активных ключевых слов")
		return nil, err
	}
	// Placeholder для usage: count matches in comments.
	usage := 0
	return &KeywordStats{Total: int(total), Active: int(active), Usage: usage}, nil
}
