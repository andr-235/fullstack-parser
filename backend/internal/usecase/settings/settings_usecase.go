package settings

import (
	"context"
	"errors"
	"strings"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"

	"backend/internal/domain/settings"
	"backend/internal/domain/users"
	"backend/internal/repository/postgres"
)

var _ users.User // blank import to satisfy compiler

var _ users.User // Используем импорт для удовлетворения компилятора

// SettingsUseCase определяет интерфейс для use cases настроек.
type SettingsUseCase interface {
	GetSettings(ctx context.Context) ([]*settings.Setting, error)
	GetSettingByKey(ctx context.Context, key string) (*settings.Setting, error)
	CreateSetting(ctx context.Context, key, value, description string, userID uuid.UUID) (*settings.Setting, error)
	UpdateSetting(ctx context.Context, key, value, description string, userID uuid.UUID) (*settings.Setting, error)
	DeleteSetting(ctx context.Context, key string, userID uuid.UUID) error
}

// SettingsUsecase содержит бизнес-логику для настроек.
type SettingsUsecase struct {
	settingRepo postgres.SettingRepository
	userRepo    postgres.UserRepository
	logger      *logrus.Logger
}

// NewSettingsUsecase создает новый usecase для настроек.
func NewSettingsUsecase(settingRepo postgres.SettingRepository, userRepo postgres.UserRepository, logger *logrus.Logger) SettingsUseCase {
	return &SettingsUsecase{
		settingRepo: settingRepo,
		userRepo:    userRepo,
		logger:      logger,
	}
}

// GetSettings получает все настройки.
func (u *SettingsUsecase) GetSettings(ctx context.Context) ([]*settings.Setting, error) {
	settings, err := u.settingRepo.List(ctx)
	if err != nil {
		u.logger.WithError(err).Error("Ошибка получения списка настроек")
		return nil, err
	}
	u.logger.Info("получение всех настроек")
	return settings, nil
}

// GetSettingByKey получает настройку по ключу.
func (u *SettingsUsecase) GetSettingByKey(ctx context.Context, key string) (*settings.Setting, error) {
	setting, err := u.settingRepo.GetByKey(ctx, key)
	if err != nil {
		u.logger.WithError(err).WithField("key", key).Error("ошибка получения настройки")
		return nil, err
	}
	return setting, nil
}

// CreateSetting создает новую настройку с проверкой роли admin.
func (u *SettingsUsecase) CreateSetting(ctx context.Context, key, value, description string, userID uuid.UUID) (*settings.Setting, error) {
	if err := u.validateKey(key); err != nil {
		u.logger.WithError(err).WithField("key", key).Warn("Недопустимый ключ настройки")
		return nil, err
	}

	user, err := u.userRepo.GetByID(userID)
	if err != nil {
		u.logger.WithError(err).WithField("user_id", userID).Error("Ошибка получения пользователя")
		return nil, err
	}
	if user == nil || user.Role != "admin" {
		return nil, errors.New("требуется роль admin")
	}

	setting := &settings.Setting{
		Key:         key,
		Value:       value,
		Description: description,
		CreatedBy:   userID,
	}

	if err := u.settingRepo.Create(ctx, setting); err != nil {
		u.logger.WithError(err).WithField("key", key).Error("Ошибка создания настройки")
		return nil, err
	}

	u.logger.WithField("key", key).Info("Настройка создана успешно")
	return setting, nil
}

// UpdateSetting обновляет настройку с проверкой роли admin.
func (u *SettingsUsecase) UpdateSetting(ctx context.Context, key, value, description string, userID uuid.UUID) (*settings.Setting, error) {
	if err := u.validateKey(key); err != nil {
		u.logger.WithError(err).WithField("key", key).Warn("Недопустимый ключ настройки")
		return nil, err
	}

	user, err := u.userRepo.GetByID(userID)
	if err != nil {
		u.logger.WithError(err).WithField("user_id", userID).Error("Ошибка получения пользователя")
		return nil, err
	}
	if user == nil || user.Role != "admin" {
		return nil, errors.New("требуется роль admin")
	}

	setting, err := u.settingRepo.GetByKey(ctx, key)
	if err != nil {
		return nil, err
	}
	if setting == nil {
		return nil, errors.New("настройка не найдена")
	}

	setting.Value = value
	setting.Description = description

	if err := u.settingRepo.Update(ctx, setting); err != nil {
		u.logger.WithError(err).WithField("key", key).Error("Ошибка обновления настройки")
		return nil, err
	}

	u.logger.WithField("key", key).Info("Настройка обновлена успешно")
	return setting, nil
}

// ListSettings возвращает список всех настроек.
func (u *SettingsUsecase) ListSettings(ctx context.Context) ([]*settings.Setting, error) {
	settings, err := u.settingRepo.List(ctx)
	if err != nil {
		u.logger.WithError(err).Error("Ошибка получения списка настроек")
		return nil, err
	}
	return settings, nil
}

// DeleteSetting удаляет настройку по ключу с проверкой роли admin.
func (u *SettingsUsecase) DeleteSetting(ctx context.Context, key string, userID uuid.UUID) error {
	if err := u.validateKey(key); err != nil {
		u.logger.WithError(err).WithField("key", key).Warn("Недопустимый ключ настройки")
		return err
	}

	user, err := u.userRepo.GetByID(userID)
	if err != nil {
		u.logger.WithError(err).WithField("user_id", userID).Error("Ошибка получения пользователя")
		return err
	}
	if user == nil || user.Role != "admin" {
		return errors.New("требуется роль admin")
	}

	if err := u.settingRepo.Delete(ctx, key); err != nil {
		u.logger.WithError(err).WithField("key", key).Error("Ошибка удаления настройки")
		return err
	}

	u.logger.WithField("key", key).Info("Настройка удалена успешно")
	return nil
}

// validateKey проверяет ключ на sensitive слова.
func (u *SettingsUsecase) validateKey(key string) error {
	sensitiveKeys := []string{"password", "secret", "token", "key", "api"}
	lowerKey := strings.ToLower(key)
	for _, sensitive := range sensitiveKeys {
		if strings.Contains(lowerKey, sensitive) {
			return errors.New("ключ содержит sensitive информацию")
		}
	}
	if len(key) == 0 || len(key) > 255 {
		return errors.New("ключ должен быть от 1 до 255 символов")
	}
	return nil
}
