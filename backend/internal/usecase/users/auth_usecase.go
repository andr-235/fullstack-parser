// Package users содержит use cases для модуля пользователей.
package users

import (
	"backend/internal/domain/users"
	"backend/internal/repository/postgres"
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"github.com/redis/go-redis/v9"
	"golang.org/x/crypto/bcrypt"
)

// AuthUseCase определяет интерфейс для use cases аутентификации.
type AuthUseCase interface {
	AuthenticateUser(identifier, password string) (*users.User, string, string, error)
	RefreshToken(refreshToken string) (string, string, error)
}

// AuthUseCaseImpl реализует AuthUseCase.
type AuthUseCaseImpl struct {
	repo        postgres.UserRepository
	redisClient *redis.Client
	jwtSecret   string
	accessTTL   time.Duration
	refreshTTL  time.Duration
}

// NewAuthUseCase создает новый экземпляр AuthUseCaseImpl.
func NewAuthUseCase(repo postgres.UserRepository, redisClient *redis.Client, jwtSecret string, accessTTL, refreshTTL time.Duration) AuthUseCase {
	return &AuthUseCaseImpl{
		repo:        repo,
		redisClient: redisClient,
		jwtSecret:   jwtSecret,
		accessTTL:   accessTTL,
		refreshTTL:  refreshTTL,
	}
}

// AuthenticateUser аутентифицирует пользователя и возвращает токены.
func (ac *AuthUseCaseImpl) AuthenticateUser(identifier, password string) (*users.User, string, string, error) {
	var user *users.User
	var err error

	// Проверка по username или email
	if strings.Contains(identifier, "@") {
		// Это email
		user, err = ac.repo.GetByEmail(identifier)
	} else {
		user, err = ac.repo.GetByUsername(identifier)
	}
	if err != nil {
		return nil, "", "", fmt.Errorf("пользователь не найден")
	}

	// Проверка пароля
	if err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(password)); err != nil {
		return nil, "", "", fmt.Errorf("неверный пароль")
	}

	// Генерация токенов
	accessToken, err := ac.generateToken(user.ID, user.Role, ac.accessTTL)
	if err != nil {
		return nil, "", "", err
	}
	refreshToken, err := ac.generateToken(user.ID, user.Role, ac.refreshTTL)
	if err != nil {
		return nil, "", "", err
	}

	ctx := context.Background()
	if err := ac.redisClient.Set(ctx, "refresh:"+user.ID.String(), refreshToken, ac.refreshTTL).Err(); err != nil {
		return nil, "", "", err
	}

	user.PasswordHash = "" // Не возвращаем пароль
	return user, accessToken, refreshToken, nil
}

// RefreshToken обновляет access token по refresh token.
func (ac *AuthUseCaseImpl) RefreshToken(refreshToken string) (string, string, error) {
	token, err := jwt.Parse(refreshToken, func(token *jwt.Token) (interface{}, error) {
		return []byte(ac.jwtSecret), nil
	})
	if err != nil || !token.Valid {
		return "", "", fmt.Errorf("неверный refresh token")
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return "", "", fmt.Errorf("неверные claims в token")
	}

	userIDStr, ok := claims["user_id"].(string)
	if !ok {
		return "", "", fmt.Errorf("неверный формат user_id в token")
	}

	userID, err := uuid.Parse(userIDStr)
	if err != nil {
		return "", "", fmt.Errorf("неверный UUID в token")
	}

	role := claims["role"].(string)

	user, err := ac.repo.GetByID(userID)
	if err != nil {
		return "", "", err
	}
	if user.Role != role {
		return "", "", fmt.Errorf("роль не совпадает")
	}

	ctx := context.Background()
	storedToken, err := ac.redisClient.Get(ctx, "refresh:"+userID.String()).Result()
	if err != nil || storedToken != refreshToken {
		return "", "", fmt.Errorf("неверный refresh token")
	}

	accessToken, err := ac.generateToken(userID, role, ac.accessTTL)
	if err != nil {
		return "", "", err
	}
	newRefreshToken, err := ac.generateToken(userID, role, ac.refreshTTL)
	if err != nil {
		return "", "", err
	}

	if err := ac.redisClient.Del(ctx, "refresh:"+userID.String()).Err(); err != nil {
		return "", "", err
	}
	if err := ac.redisClient.Set(ctx, "refresh:"+userID.String(), newRefreshToken, ac.refreshTTL).Err(); err != nil {
		return "", "", err
	}

	return accessToken, newRefreshToken, nil
}

// generateToken генерирует JWT токен.
func (ac *AuthUseCaseImpl) generateToken(userID uuid.UUID, role string, ttl time.Duration) (string, error) {
	claims := jwt.MapClaims{
		"user_id": userID.String(),
		"role":    role,
		"exp":     time.Now().Add(ttl).Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(ac.jwtSecret))
}
