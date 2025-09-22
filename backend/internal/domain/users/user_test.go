package users

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestUser_NewUser(t *testing.T) {
	// Тест создания нового пользователя
	id := uuid.New()
	username := "testuser"
	email := "test@example.com"
	passwordHash := "hashedpassword"
	role := "user"
	now := time.Now()

	user := User{
		ID:           id,
		Username:     username,
		Email:        email,
		PasswordHash: passwordHash,
		Role:         role,
		CreatedAt:    now,
		UpdatedAt:    now,
	}

	assert.Equal(t, id, user.ID, "ID должен совпадать")
	assert.Equal(t, username, user.Username, "Username должен совпадать")
	assert.Equal(t, email, user.Email, "Email должен совпадать")
	assert.Equal(t, passwordHash, user.PasswordHash, "PasswordHash должен совпадать")
	assert.Equal(t, role, user.Role, "Role должен совпадать")
	assert.Equal(t, now, user.CreatedAt, "CreatedAt должен совпадать")
	assert.Equal(t, now, user.UpdatedAt, "UpdatedAt должен совпадать")
}

func TestUser_JSONMarshal(t *testing.T) {
	// Тест marshal/unmarshal JSON - PasswordHash не должен экспортироваться
	id := uuid.New()
	user := User{
		ID:           id,
		Username:     "testuser",
		Email:        "test@example.com",
		PasswordHash: "secret",
		Role:         "user",
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}

	jsonData, err := json.Marshal(user)
	assert.NoError(t, err)

	var unmarshaled User
	err = json.Unmarshal(jsonData, &unmarshaled)
	assert.NoError(t, err)

	assert.Equal(t, id, unmarshaled.ID)
	assert.Equal(t, "testuser", unmarshaled.Username)
	assert.Equal(t, "test@example.com", unmarshaled.Email)
	assert.Equal(t, "", unmarshaled.PasswordHash, "PasswordHash не должен быть в JSON")
	assert.Equal(t, "user", unmarshaled.Role)
}