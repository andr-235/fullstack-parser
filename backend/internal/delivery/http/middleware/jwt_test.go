package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestJWTAuth_ValidToken(t *testing.T) {
	secret := "test-secret"
	mw := JWTAuth(secret)

	w := httptest.NewRecorder()
	r := httptest.NewRequest("GET", "/test", nil)

	// Create a valid token
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id": uuid.New().String(),
		"role":    "user",
	})
	tokenString, _ := token.SignedString([]byte(secret))

	r.Header.Set("Authorization", "Bearer "+tokenString)

	c, _ := gin.CreateTestContext(w)
	c.Request = r

	mw(c)

	assert.Equal(t, http.StatusOK, w.Code)
	userID, exists := c.Get(UserIDKey)
	assert.True(t, exists)
	assert.NotNil(t, userID)
	role, exists := c.Get(RoleKey)
	assert.True(t, exists)
	assert.Equal(t, "user", role)
}

func TestJWTAuth_MissingToken(t *testing.T) {
	secret := "test-secret"
	mw := JWTAuth(secret)

	w := httptest.NewRecorder()
	r := httptest.NewRequest("GET", "/test", nil)

	c, _ := gin.CreateTestContext(w)
	c.Request = r

	mw(c)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
	assert.Contains(t, w.Body.String(), "токен не предоставлен")
	assert.Equal(t, gin.StatusAborted, c.Writer.Status())
}

func TestJWTAuth_InvalidFormat(t *testing.T) {
	secret := "test-secret"
	mw := JWTAuth(secret)

	w := httptest.NewRecorder()
	r := httptest.NewRequest("GET", "/test", nil)
	r.Header.Set("Authorization", "Invalid token")

	c, _ := gin.CreateTestContext(w)
	c.Request = r

	mw(c)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
	assert.Contains(t, w.Body.String(), "неверный формат токена")
	assert.Equal(t, gin.StatusAborted, c.Writer.Status())
}

func TestJWTAuth_InvalidToken(t *testing.T) {
	secret := "test-secret"
	mw := JWTAuth(secret)

	w := httptest.NewRecorder()
	r := httptest.NewRequest("GET", "/test", nil)
	r.Header.Set("Authorization", "Bearer invalid.token")

	c, _ := gin.CreateTestContext(w)
	c.Request = r

	mw(c)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
	assert.Contains(t, w.Body.String(), "неверный токен")
	assert.Equal(t, gin.StatusAborted, c.Writer.Status())
}

func TestRoleAuth_AdminOnly(t *testing.T) {
	secret := "test-secret"
	mw := RoleAuth("admin")

	w := httptest.NewRecorder()
	r := httptest.NewRequest("GET", "/test", nil)

	// Valid token with admin role
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id": uuid.New().String(),
		"role":    "admin",
	})
	tokenString, _ := token.SignedString([]byte(secret))

	r.Header.Set("Authorization", "Bearer "+tokenString)

	c, _ := gin.CreateTestContext(w)
	c.Request = r
	c.Set(RoleKey, "admin")

	mw(c)

	assert.Equal(t, http.StatusOK, w.Code)
}

func TestRoleAuth_NotAdmin(t *testing.T) {
	secret := "test-secret"
	mw := RoleAuth("admin")

	w := httptest.NewRecorder()
	r := httptest.NewRequest("GET", "/test", nil)

	// Valid token with user role
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id": uuid.New().String(),
		"role":    "user",
	})
	tokenString, _ := token.SignedString([]byte(secret))

	r.Header.Set("Authorization", "Bearer "+tokenString)

	c, _ := gin.CreateTestContext(w)
	c.Request = r
	c.Set(RoleKey, "user")

	mw(c)

	assert.Equal(t, http.StatusForbidden, w.Code)
	assert.Contains(t, w.Body.String(), "недостаточно прав")
	assert.Equal(t, gin.StatusAborted, c.Writer.Status())
}