// Package postgres содержит реализации репозиториев для PostgreSQL.
package postgres

import (
	"context"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"

	"backend/internal/domain/settings"
)

// SettingRepository определяет интерфейс для работы с настройками в БД.
type SettingRepository interface {
	Create(ctx context.Context, setting *settings.Setting) error
	GetByKey(ctx context.Context, key string) (*settings.Setting, error)
	Update(ctx context.Context, setting *settings.Setting) error
	List(ctx context.Context) ([]*settings.Setting, error)
	Delete(ctx context.Context, key string) error
}

// SettingPostgresRepository реализует SettingRepository с использованием GORM.
type SettingPostgresRepository struct {
	db *gorm.DB
}

// NewSettingPostgresRepository создает новый репозиторий настроек.
func NewSettingPostgresRepository(db *gorm.DB) *SettingPostgresRepository {
	return &SettingPostgresRepository{db: db}
}

// Create создает новую настройку в БД.
func (r *SettingPostgresRepository) Create(ctx context.Context, setting *settings.Setting) error {
	if err := r.db.WithContext(ctx).Create(setting).Error; err != nil {
		logrus.WithError(err).WithField("key", setting.Key).Error("Ошибка создания настройки")
		return err
	}
	return nil
}

// GetByKey получает настройку по ключу.
func (r *SettingPostgresRepository) GetByKey(ctx context.Context, key string) (*settings.Setting, error) {
	var setting settings.Setting
	if err := r.db.WithContext(ctx).Where("key = ?", key).First(&setting).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, nil // Не найдено - не ошибка
		}
		logrus.WithError(err).WithField("key", key).Error("Ошибка получения настройки по ключу")
		return nil, err
	}
	return &setting, nil
}

// Update обновляет настройку.
func (r *SettingPostgresRepository) Update(ctx context.Context, setting *settings.Setting) error {
	if err := r.db.WithContext(ctx).Save(setting).Error; err != nil {
		logrus.WithError(err).WithField("key", setting.Key).Error("Ошибка обновления настройки")
		return err
	}
	return nil
}

// List возвращает список всех настроек.
func (r *SettingPostgresRepository) List(ctx context.Context) ([]*settings.Setting, error) {
	var settings []*settings.Setting
	if err := r.db.WithContext(ctx).Find(&settings).Error; err != nil {
		logrus.WithError(err).Error("Ошибка получения списка настроек")
		return nil, err
	}
	return settings, nil
}

// Delete удаляет настройку по ключу.
func (r *SettingPostgresRepository) Delete(ctx context.Context, key string) error {
	if err := r.db.WithContext(ctx).Where("key = ?", key).Delete(&settings.Setting{}).Error; err != nil {
		logrus.WithError(err).WithField("key", key).Error("Ошибка удаления настройки")
		return err
	}
	return nil
}