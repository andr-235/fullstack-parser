// Package users содержит handlers для эндпоинтов пользователей.
package users

import (
	"net/http"
	"strconv"

	"backend/internal/usecase/users"

	"github.com/gin-gonic/gin"
)

// UserHandler представляет handlers для пользователей.
type UserHandler struct {
	userUseCase users.UserUseCase
}

// NewUserHandler создает новый экземпляр UserHandler.
func NewUserHandler(userUseCase users.UserUseCase) *UserHandler {
	return &UserHandler{userUseCase: userUseCase}
}

// GetUser получает пользователя по ID.
func (h *UserHandler) GetUser(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "неверный ID"})
		return
	}

	user, err := h.userUseCase.GetUser(uint(id))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "пользователь не найден"})
		return
	}

	c.JSON(http.StatusOK, user)
}

// UpdateUser обновляет пользователя.
func (h *UserHandler) UpdateUser(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "неверный ID"})
		return
	}

	var req struct {
		Username string `json:"username"`
		Email    string `json:"email"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := h.userUseCase.UpdateUser(uint(id), req.Username, req.Email)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, user)
}

// DeleteUser удаляет пользователя.
func (h *UserHandler) DeleteUser(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "неверный ID"})
		return
	}

	if err := h.userUseCase.DeleteUser(uint(id)); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "пользователь не найден"})
		return
	}

	c.JSON(http.StatusNoContent, nil)
}

// ListUsers получает список пользователей (для admin).
func (h *UserHandler) ListUsers(c *gin.Context) {
	// Здесь можно добавить пагинацию, но для простоты возвращаем всех
	// В реальности использовать repo.List() с пагинацией
	c.JSON(http.StatusOK, gin.H{"users": []interface{}{}}) // Заглушка, реализовать позже
}