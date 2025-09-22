// Package keywords содержит HTTP handlers для модуля ключевых слов.
// Handlers используют Gin и интегрируются с use cases.

package keywords

import (
	"net/http"
	"strconv"

	"backend/internal/usecase/keywords"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

// Handler - структура для handlers ключевых слов.
type Handler struct {
	useCase keywords.UseCase
	logger  *logrus.Logger
}

// NewHandler создает новый экземпляр Handler.
func NewHandler(useCase keywords.UseCase, logger *logrus.Logger) *Handler {
	return &Handler{
		useCase: useCase,
		logger:  logger,
	}
}

// RegisterRoutes регистрирует роуты для ключевых слов.
func (h *Handler) RegisterRoutes(r *gin.Engine) {
	keywordsGroup := r.Group("/api/v1/keywords")
	keywordsGroup.Use(AuthMiddleware()) // Placeholder для JWT middleware.
	{
		keywordsGroup.GET("", h.listKeywords)
		keywordsGroup.GET("/:id", h.getKeyword)
		keywordsGroup.POST("", h.createKeyword)
		keywordsGroup.PUT("/:id", h.updateKeyword)
		keywordsGroup.DELETE("/:id", h.deleteKeyword)
		keywordsGroup.PATCH("/:id/activate", h.activateKeyword)
		keywordsGroup.PATCH("/:id/deactivate", h.deactivateKeyword)
		keywordsGroup.GET("/stats", h.getStats)
	}
}

// AuthMiddleware - placeholder для JWT middleware с проверкой роли admin для CRUD.
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Placeholder: проверка JWT и роли admin.
		c.Next()
	}
}

// listKeywords обрабатывает GET /api/v1/keywords.
func (h *Handler) listKeywords(c *gin.Context) {
	activeOnlyStr := c.Query("active")
	activeOnly := activeOnlyStr == "true"

	list, err := h.useCase.ListKeywords(c.Request.Context(), activeOnly)
	if err != nil {
		h.logger.WithError(err).Error("ошибка получения списка")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "внутренняя ошибка сервера"})
		return
	}

	c.JSON(http.StatusOK, list)
}

// getKeyword обрабатывает GET /api/v1/keywords/{id}.
func (h *Handler) getKeyword(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "некорректный ID"})
		return
	}

	k, err := h.useCase.GetKeyword(c.Request.Context(), uint(id))
	if err != nil {
		h.logger.WithError(err).WithField("id", id).Error("ошибка получения ключевого слова")
		c.JSON(http.StatusNotFound, gin.H{"error": "ключ не найден"})
		return
	}

	c.JSON(http.StatusOK, k)
}

// createKeyword обрабатывает POST /api/v1/keywords.
func (h *Handler) createKeyword(c *gin.Context) {
	var req struct {
		Text        string `json:"text" binding:"required"`
		Description string `json:"description"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "некорректный запрос"})
		return
	}

	k, err := h.useCase.CreateKeyword(c.Request.Context(), req.Text, req.Description)
	if err != nil {
		h.logger.WithError(err).Error("ошибка создания ключевого слова")
		if err.Error() == "текст не может быть пустым" || err.Error() == "текст не может превышать 255 символов" {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		if err.Error() == "текст должен содержать минимум 3 символа" {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusConflict, gin.H{"error": "конфликт, ключ уже существует"})
		return
	}

	c.JSON(http.StatusCreated, k)
}

// updateKeyword обрабатывает PUT /api/v1/keywords/{id}.
func (h *Handler) updateKeyword(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "некорректный ID"})
		return
	}

	var req struct {
		Text        string `json:"text" binding:"required"`
		Description string `json:"description"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "некорректный запрос"})
		return
	}

	k, err := h.useCase.UpdateKeyword(c.Request.Context(), uint(id), req.Text, req.Description)
	if err != nil {
		h.logger.WithError(err).Error("ошибка обновления ключевого слова")
		c.JSON(http.StatusConflict, gin.H{"error": "конфликт, ключ уже существует"})
		return
	}

	c.JSON(http.StatusOK, k)
}

// deleteKeyword обрабатывает DELETE /api/v1/keywords/{id}.
func (h *Handler) deleteKeyword(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "некорректный ID"})
		return
	}

	if err := h.useCase.DeleteKeyword(c.Request.Context(), uint(id)); err != nil {
		h.logger.WithError(err).Error("ошибка удаления ключевого слова")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "внутренняя ошибка сервера"})
		return
	}

	c.JSON(http.StatusNoContent, nil)
}

// activateKeyword обрабатывает PATCH /api/v1/keywords/{id}/activate.
func (h *Handler) activateKeyword(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "некорректный ID"})
		return
	}

	if err := h.useCase.ActivateKeyword(c.Request.Context(), uint(id)); err != nil {
		h.logger.WithError(err).Error("ошибка активации ключевого слова")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "внутренняя ошибка сервера"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "ключ активировано"})
}

// deactivateKeyword обрабатывает PATCH /api/v1/keywords/{id}/deactivate.
func (h *Handler) deactivateKeyword(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "некорректный ID"})
		return
	}

	if err := h.useCase.DeactivateKeyword(c.Request.Context(), uint(id)); err != nil {
		h.logger.WithError(err).Error("ошибка деактивации ключевого слова")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "внутренняя ошибка сервера"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "ключ деактивировано"})
}

// getStats обрабатывает GET /api/v1/keywords/stats.
func (h *Handler) getStats(c *gin.Context) {
	stats, err := h.useCase.GetKeywordStats(c.Request.Context())
	if err != nil {
		h.logger.WithError(err).Error("ошибка получения статистики")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "внутренняя ошибка сервера"})
		return
	}

	c.JSON(http.StatusOK, stats)
}