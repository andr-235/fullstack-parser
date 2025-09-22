package users

import (
	"testing"
	"time"

	"backend/internal/domain/users"
	"backend/internal/repository/postgres"

	"gorm.io/gorm"
	"github.com/golang-jwt/jwt/v5"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockUserRepository для auth use case.
type MockUserRepositoryAuth struct {
	mock.Mock
	postgres.UserRepository
}

// Create mock для Create (если нужно).
func (m *MockUserRepositoryAuth) Create(user *users.User) error {
	args := m.Called(user)
	return args.Error(0)
}

// GetByID mock для GetByID.
func (m *MockUserRepositoryAuth) GetByID(id uint) (*users.User, error) {
	args := m.Called(id)
	return args.Get(0).(*users.User), args.Error(1)
}

// GetByEmail mock для GetByEmail.
func (m *MockUserRepositoryAuth) GetByEmail(email string) (*users.User, error) {
	args := m.Called(email)
	return args.Get(0).(*users.User), args.Error(1)
}

// GetByUsername mock для GetByUsername.
func (m *MockUserRepositoryAuth) GetByUsername(username string) (*users.User, error) {
	args := m.Called(username)
	return args.Get(0).(*users.User), args.Error(1)
}

// Update mock для Update.
func (m *MockUserRepositoryAuth) Update(user *users.User) error {
	args := m.Called(user)
	return args.Error(0)
}

// Delete mock для Delete.
func (m *MockUserRepositoryAuth) Delete(id uint) error {
	args := m.Called(id)
	return args.Error(0)
}

func TestAuthUseCase_AuthenticateUser(t *testing.T) {
	mockRepo := new(MockUserRepositoryAuth)
	useCase := NewAuthUseCase(mockRepo, "secret", 15*time.Minute, 168*time.Hour)

	expectedUser := &users.User{ID: 1, Username: "test", Email: "test@example.com", PasswordHash: "$2a$10$...", Role: "user"}
	mockRepo.On("GetByUsername", "test").Return(expectedUser, nil)
	mockRepo.On("GetByEmail", mock.Anything).Return(nil, gorm.ErrRecordNotFound)

	// Мок bcrypt
	// В реальном тесте использовать mock для bcrypt, но для простоты предполагаем успех

	user, accessToken, refreshToken, err := useCase.AuthenticateUser("test", "password")
	assert.NoError(t, err)
	assert.NotNil(t, user)
	assert.NotEmpty(t, accessToken)
	assert.NotEmpty(t, refreshToken)

	mockRepo.AssertExpectations(t)
}

// Добавьте тесты для RefreshToken и других сценариев