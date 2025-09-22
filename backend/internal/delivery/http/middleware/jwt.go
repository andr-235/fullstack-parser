// Package middleware содержит middleware для HTTP handlers.
package middleware

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
)

// Константы для ключей контекста
const (
	UserIDKey = "user_id"
	RoleKey   = "role"
)

// JWTAuth middleware проверяет JWT токен и устанавливает user_id и role в context.
func JWTAuth(jwtSecret string) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "токен не предоставлен"})
			c.Abort()
			return
		}

		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "неверный формат токена"})
			c.Abort()
			return
		}

		token, err := jwt.Parse(parts[1], func(token *jwt.Token) (interface{}, error) {
			return []byte(jwtSecret), nil
		})
		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "неверный токен"})
			c.Abort()
			return
		}

		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "неверные claims"})
			c.Abort()
			return
		}

		userIDStr, ok := claims["user_id"].(string)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "неверный формат user_id"})
			c.Abort()
			return
		}

		userID, err := uuid.Parse(userIDStr)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "неверный UUID в токене"})
			c.Abort()
			return
		}

		role := claims["role"].(string)

		c.Set(UserIDKey, userID)
		c.Set(RoleKey, role)
		c.Next()
	}
}

// RoleAuth middleware проверяет роль пользователя.
func RoleAuth(requiredRole string) gin.HandlerFunc {
	return func(c *gin.Context) {
		role, exists := c.Get(RoleKey)
		if !exists || role.(string) != requiredRole {
			c.JSON(http.StatusForbidden, gin.H{"error": "недостаточно прав"})
			c.Abort()
			return
		}
		c.Next()
	}
}

// AdminOnly middleware проверяет, что пользователь является администратором.
func AdminOnly() gin.HandlerFunc {
	return RoleAuth("admin")
}
