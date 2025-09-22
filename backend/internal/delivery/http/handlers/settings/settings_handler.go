package settings

import (
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"

	"backend/internal/delivery/http/middleware"
	"backend/internal/usecase/settings"
)

// Ошибки аутентификации
var (
	ErrUnauthorized  = errors.New("не авторизован")
	ErrInvalidUserID = errors.New("неверный ID пользователя")
)

// Константы для ролей
const (
	AdminRole = "admin"
)

// SettingsHandler обрабатывает HTTP-запросы для настроек.
type SettingsHandler struct {
	usecase *settings.SettingsUsecase
	logger  *logrus.Logger
}

// CreateSettingRequest представляет запрос на создание настройки.
type CreateSettingRequest struct {
	Key         string `json:"key" binding:"required"`
	Value       string `json:"value" binding:"required"`
	Description string `json:"description"`
}

// UpdateSettingRequest представляет запрос на обновление настройки.
type UpdateSettingRequest struct {
	Value       string `json:"value" binding:"required"`
	Description string `json:"description"`
}

// ErrorResponse представляет стандартный ответ об ошибке.
type ErrorResponse struct {
	Error string `json:"error"`
}

// NewSettingsHandler создает новый handler для настроек.
func NewSettingsHandler(usecase *settings.SettingsUsecase, logger *logrus.Logger) *SettingsHandler {
	return &SettingsHandler{
		usecase: usecase,
		logger:  logger,
	}
}

// getUserIDFromContext извлекает ID пользователя из контекста.
func (h *SettingsHandler) getUserIDFromContext(c *gin.Context) (uuid.UUID, error) {
	userID, exists := c.Get(middleware.UserIDKey)
	if !exists {
		return uuid.Nil, ErrUnauthorized
	}

	userIDUUID, ok := userID.(uuid.UUID)
	if !ok {
		return uuid.Nil, ErrInvalidUserID
	}

	return userIDUUID, nil
}

// sendErrorResponse отправляет стандартизированный ответ об ошибке.
func (h *SettingsHandler) sendErrorResponse(c *gin.Context, statusCode int, message string) {
	c.JSON(statusCode, ErrorResponse{Error: message})
}

// sendInternalServerError отправляет ответ о внутренней ошибке сервера.
func (h *SettingsHandler) sendInternalServerError(c *gin.Context, err error, operation string) {
	h.logger.WithError(err).Error(operation)
	h.sendErrorResponse(c, http.StatusInternalServerError, "Внутренняя ошибка сервера")
}

// handleSettingError обрабатывает ошибки операций с настройками.
func (h *SettingsHandler) handleSettingError(c *gin.Context, err error, operation, key string) {
	h.logger.WithError(err).WithField("key", key).Error(operation)

	switch err.Error() {
	case "требуется роль admin":
		h.sendErrorResponse(c, http.StatusForbidden, "Доступ запрещен")
	case "настройка не найдена":
		h.sendErrorResponse(c, http.StatusNotFound, "Настройка не найдена")
	default:
		h.sendErrorResponse(c, http.StatusBadRequest, err.Error())
	}
}

// GetSettings возвращает список настроек.
func (h *SettingsHandler) GetSettings(c *gin.Context) {
	settingsList, err := h.usecase.ListSettings(c.Request.Context())
	if err != nil {
		h.sendInternalServerError(c, err, "Ошибка получения списка настроек")
		return
	}
	c.JSON(http.StatusOK, settingsList)
}

// GetSettingByKey возвращает настройку по ключу.
func (h *SettingsHandler) GetSettingByKey(c *gin.Context) {
	key := c.Param("key")
	setting, err := h.usecase.GetSettingByKey(c.Request.Context(), key)
	if err != nil {
		if err.Error() == "настройка не найдена" {
			h.sendErrorResponse(c, http.StatusNotFound, "Настройка не найдена")
		} else {
			h.sendInternalServerError(c, err, "Ошибка получения настройки")
		}
		return
	}
	c.JSON(http.StatusOK, setting)
}

// CreateSetting создает новую настройку.
func (h *SettingsHandler) CreateSetting(c *gin.Context) {
	var req CreateSettingRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.WithError(err).Error("Ошибка валидации запроса создания настройки")
		h.sendErrorResponse(c, http.StatusBadRequest, "Неверный формат запроса")
		return
	}

	userID, err := h.getUserIDFromContext(c)
	if err != nil {
		h.sendErrorResponse(c, http.StatusUnauthorized, err.Error())
		return
	}

	setting, err := h.usecase.CreateSetting(c.Request.Context(), req.Key, req.Value, req.Description, userID)
	if err != nil {
		h.handleSettingError(c, err, "Ошибка создания настройки", req.Key)
		return
	}

	c.JSON(http.StatusCreated, setting)
}

// UpdateSetting обновляет настройку.
func (h *SettingsHandler) UpdateSetting(c *gin.Context) {
	key := c.Param("key")
	var req UpdateSettingRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.WithError(err).WithField("key", key).Error("Ошибка валидации запроса обновления настройки")
		h.sendErrorResponse(c, http.StatusBadRequest, "Неверный формат запроса")
		return
	}

	userID, err := h.getUserIDFromContext(c)
	if err != nil {
		h.sendErrorResponse(c, http.StatusUnauthorized, err.Error())
		return
	}

	setting, err := h.usecase.UpdateSetting(c.Request.Context(), key, req.Value, req.Description, userID)
	if err != nil {
		h.handleSettingError(c, err, "Ошибка обновления настройки", key)
		return
	}

	c.JSON(http.StatusOK, setting)
}

// DeleteSetting удаляет настройку.
func (h *SettingsHandler) DeleteSetting(c *gin.Context) {
	key := c.Param("key")

	userID, err := h.getUserIDFromContext(c)
	if err != nil {
		h.sendErrorResponse(c, http.StatusUnauthorized, err.Error())
		return
	}

	err = h.usecase.DeleteSetting(c.Request.Context(), key, userID)
	if err != nil {
		h.handleSettingError(c, err, "Ошибка удаления настройки", key)
		return
	}

	c.JSON(http.StatusNoContent, nil)
}
