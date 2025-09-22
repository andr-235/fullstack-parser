// Package auth содержит handlers для эндпоинтов аутентификации.
package auth

import (
	"net/http"

	"backend/internal/usecase/users"

	"github.com/gin-gonic/gin"
)

// AuthHandler представляет handlers для аутентификации.
type AuthHandler struct {
	authUseCase users.AuthUseCase
	userUseCase users.UserUseCase
}

// NewAuthHandler создает новый экземпляр AuthHandler.
func NewAuthHandler(authUseCase users.AuthUseCase, userUseCase users.UserUseCase) *AuthHandler {
	return &AuthHandler{
		authUseCase: authUseCase,
		userUseCase: userUseCase,
	}
}

// RegisterRequest представляет запрос на регистрацию.
type RegisterRequest struct {
	Username string `json:"username" binding:"required"`
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=8"`
}

// RegisterResponse представляет ответ на регистрацию.
type RegisterResponse struct {
	AccessToken  string   `json:"access_token"`
	RefreshToken string   `json:"refresh_token"`
	User         UserInfo `json:"user"`
}

// UserInfo представляет информацию о пользователе.
type UserInfo struct {
	ID       uint   `json:"id"`
	Username string `json:"username"`
	Email    string `json:"email"`
	Role     string `json:"role"`
}

// Register регистрирует нового пользователя.
func (h *AuthHandler) Register(c *gin.Context) {
	var req RegisterRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		h.sendErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	// Создание пользователя
	user, err := h.userUseCase.CreateUser(req.Username, req.Email, req.Password)
	if err != nil {
		h.sendErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	// Генерация токенов после создания
	_, accessToken, refreshToken, err := h.authUseCase.AuthenticateUser(req.Username, req.Password)
	if err != nil {
		h.sendErrorResponse(c, http.StatusInternalServerError, "ошибка генерации токенов")
		return
	}

	response := RegisterResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		User: UserInfo{
			ID:       user.ID.String(),
			Username: user.Username,
			Email:    user.Email,
			Role:     user.Role,
		},
	}

	c.JSON(http.StatusCreated, response)
}

// LoginRequest представляет запрос на вход.
type LoginRequest struct {
	Identifier string `json:"identifier" binding:"required"`
	Password   string `json:"password" binding:"required"`
}

// LoginResponse представляет ответ на вход.
type LoginResponse struct {
	AccessToken  string   `json:"access_token"`
	RefreshToken string   `json:"refresh_token"`
	User         UserInfo `json:"user"`
}

// Login аутентифицирует пользователя.
func (h *AuthHandler) Login(c *gin.Context) {
	var req LoginRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		h.sendErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	user, accessToken, refreshToken, err := h.authUseCase.AuthenticateUser(req.Identifier, req.Password)
	if err != nil {
		h.sendErrorResponse(c, http.StatusUnauthorized, err.Error())
		return
	}

	response := LoginResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		User: UserInfo{
			ID:       user.ID.String(),
			Username: user.Username,
			Email:    user.Email,
			Role:     user.Role,
		},
	}

	c.JSON(http.StatusOK, response)
}

// RefreshRequest представляет запрос на обновление токенов.
type RefreshRequest struct {
	RefreshToken string `json:"refresh_token" binding:"required"`
}

// RefreshResponse представляет ответ на обновление токенов.
type RefreshResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
}

// Refresh обновляет токены.
func (h *AuthHandler) Refresh(c *gin.Context) {
	var req RefreshRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		h.sendErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	accessToken, refreshToken, err := h.authUseCase.RefreshToken(req.RefreshToken)
	if err != nil {
		h.sendErrorResponse(c, http.StatusUnauthorized, err.Error())
		return
	}

	response := RefreshResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
	}

	c.JSON(http.StatusOK, response)
}

// sendErrorResponse отправляет стандартизированный ответ об ошибке.
func (h *AuthHandler) sendErrorResponse(c *gin.Context, statusCode int, message string) {
	c.JSON(statusCode, gin.H{"error": message})
}
