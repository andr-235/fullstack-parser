package users

import (
	"testing"
	"time"

	"backend/internal/domain/users"
	"backend/internal/repository/postgres"

	"github.com/google/uuid"
	"gorm.io/gorm"
	"github.com/golang-jwt/jwt/v5"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"golang.org/x/crypto/bcrypt"
)

// MockUserRepositoryAuth для auth use case.
type MockUserRepositoryAuth struct {
	mock.Mock
	postgres.UserRepository
}

// Create mock для Create (если нужно).
func (m *MockUserRepositoryAuth) Create(user *users.User) error {
	args := m.Called(user)
	return args.Error(0)
}

// GetByID mock для GetByID (исправлено на uuid.UUID).
func (m *MockUserRepositoryAuth) GetByID(id uuid.UUID) (*users.User, error) {
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
func (m *MockUserRepositoryAuth) Delete(id uuid.UUID) error {
	args := m.Called(id)
	return args.Error(0)
}

func TestAuthUseCase_AuthenticateUser(t *testing.T) {
	mockRepo := new(MockUserRepositoryAuth)
	useCase := NewAuthUseCase(mockRepo, "secret", 15*time.Minute, 168*time.Hour)

	// Создаем тестового пользователя с хэшированным паролем
	password := "testpassword"
	passwordHash, _ := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	expectedUser := &users.User{
		ID:           uuid.New(),
		Username:     "testuser",
		Email:        "test@example.com",
		PasswordHash: string(passwordHash),
		Role:         "user",
	}

	tests := []struct {
		name          string
		identifier    string
		password      string
		setupMock     func()
		expectedUser  *users.User
		expectedErr   string
	}{
		{
			name:       "success with username",
			identifier: "testuser",
			password:   "testpassword",
			setupMock: func() {
				mockRepo.On("GetByUsername", "testuser").Return(expectedUser, nil)
			},
			expectedUser: &users.User{
				ID:       expectedUser.ID,
				Username: "testuser",
				Email:    "test@example.com",
				Role:     "user",
			},
		},
		{
			name:       "success with email",
			identifier: "test@example.com",
			password:   "testpassword",
			setupMock: func() {
				mockRepo.On("GetByEmail", "test@example.com").Return(expectedUser, nil)
			},
			expectedUser: &users.User{
				ID:       expectedUser.ID,
				Username: "testuser",
				Email:    "test@example.com",
				Role:     "user",
			},
		},
		{
			name:       "invalid password",
			identifier: "testuser",
			password:   "wrongpassword",
			setupMock: func() {
				mockRepo.On("GetByUsername", "testuser").Return(expectedUser, nil)
			},
			expectedErr: "неверный пароль",
		},
		{
			name:       "user not found by username",
			identifier: "nonexistent",
			password:   "testpassword",
			setupMock: func() {
				mockRepo.On("GetByUsername", "nonexistent").Return(nil, gorm.ErrRecordNotFound)
			},
			expectedErr: "пользователь не найден",
		},
		{
			name:       "user not found by email",
			identifier: "nonexistent@example.com",
			password:   "testpassword",
			setupMock: func() {
				mockRepo.On("GetByEmail", "nonexistent@example.com").Return(nil, gorm.ErrRecordNotFound)
			},
			expectedErr: "пользователь не найден",
		},
		{
			name:       "invalid identifier (neither email nor username)",
			identifier: "invalid123",
			password:   "testpassword",
			setupMock: func() {
				mockRepo.On("GetByUsername", "invalid123").Return(nil, gorm.ErrRecordNotFound)
			},
			expectedErr: "пользователь не найден",
		},
		{
			name:       "empty identifier",
			identifier: "",
			password:   "testpassword",
			setupMock:  func() {}, // No mock calls
			expectedErr: "пользователь не найден", // Since GetByUsername("") will likely fail
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.setupMock()

			user, accessToken, refreshToken, err := useCase.AuthenticateUser(tt.identifier, tt.password)

			if tt.expectedErr != "" {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.expectedErr)
				assert.Nil(t, user)
				assert.Empty(t, accessToken)
				assert.Empty(t, refreshToken)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expectedUser, user)
				assert.NotEmpty(t, accessToken)
				assert.NotEmpty(t, refreshToken)
				// Проверяем, что пароль не возвращается
				assert.Empty(t, user.PasswordHash)
			}

			mockRepo.AssertExpectations(t)
			mockRepo.AssertNumberOfCalls(t, "GetByUsername", 1) // Для случаев username
			// Для email calls будут отличаться, но AssertExpectations покрывает
		})
	}
}

func TestAuthUseCase_RefreshToken(t *testing.T) {
	mockRepo := new(MockUserRepositoryAuth)
	useCase := NewAuthUseCase(mockRepo, "secret", 15*time.Minute, 168*time.Hour)

	userID := uuid.New()
	expectedUser := &users.User{
		ID:       userID,
		Username: "testuser",
		Email:    "test@example.com",
		Role:     "user",
	}

	// Генерируем валидный refresh token
	refreshToken, _ := useCase.(*AuthUseCaseImpl).generateToken(userID, "user", 168*time.Hour)

	// Для expired token: создаем с прошлым exp
	expiredClaims := jwt.MapClaims{
		"user_id": userID.String(),
		"role":    "user",
		"exp":     time.Now().Add(-1 * time.Hour).Unix(),
	}
	expiredToken := jwt.NewWithClaims(jwt.SigningMethodHS256, expiredClaims)
	expiredTokenStr, _ := expiredToken.SignedString([]byte("secret"))

	// Invalid token: malformed
	invalidToken := "invalid.token.here"

	tests := []struct {
		name         string
		refreshToken string
		setupMock    func()
		expectedErr  string
	}{
		{
			name:         "success",
			refreshToken: refreshToken,
			setupMock: func() {
				mockRepo.On("GetByID", userID).Return(expectedUser, nil)
			},
		},
		{
			name:         "invalid token",
			refreshToken: invalidToken,
			setupMock:    func() {},
			expectedErr:  "неверный refresh token",
		},
		{
			name:         "expired token",
			refreshToken: expiredTokenStr,
			setupMock:    func() {},
			expectedErr:  "token is expired", // jwt err
		},
		{
			name:         "user not found",
			refreshToken: refreshToken,
			setupMock: func() {
				mockRepo.On("GetByID", userID).Return(nil, gorm.ErrRecordNotFound)
			},
			expectedErr: "record not found",
		},
		{
			name:         "wrong role",
			refreshToken: refreshToken,
			setupMock: func() {
				wrongUser := *expectedUser
				wrongUser.Role = "admin"
				mockRepo.On("GetByID", userID).Return(&wrongUser, nil)
			},
			expectedErr: "роль не совпадает",
		},
		{
			name:         "invalid claims",
			refreshToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoidXNlciJ9.invalid", // No user_id
			setupMock:    func() {},
			expectedErr:  "неверные claims в token",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.setupMock()

			accessToken, newRefreshToken, err := useCase.RefreshToken(tt.refreshToken)

			if tt.expectedErr != "" {
				assert.Error(t, err)
				if tt.expectedErr == "неверный refresh token" || tt.expectedErr == "token is expired" {
					assert.Contains(t, err.Error(), tt.expectedErr)
				} else {
					assert.Contains(t, err.Error(), tt.expectedErr)
				}
				assert.Empty(t, accessToken)
				assert.Empty(t, newRefreshToken)
			} else {
				assert.NoError(t, err)
				assert.NotEmpty(t, accessToken)
				assert.NotEmpty(t, newRefreshToken)
			}

			mockRepo.AssertExpectations(t)
		})
	}
}

// Тест для generateToken (как private метод, тестируем через reflection или отдельно, но для покрытия используем в выше)
func TestAuthUseCase_generateToken(t *testing.T) {
	useCase := NewAuthUseCase(nil, "secret", 15*time.Minute, 168*time.Hour).(*AuthUseCaseImpl)

	userID := uuid.New()
	role := "user"
	ttl := 5 * time.Minute

	token, err := useCase.generateToken(userID, role, ttl)

	assert.NoError(t, err)
	assert.NotEmpty(t, token)

	// Валидация токена
	parsedToken, parseErr := jwt.Parse(token, func(token *jwt.Token) (interface{}, error) {
		return []byte("secret"), nil
	})
	assert.NoError(t, parseErr)
	assert.True(t, parsedToken.Valid)

	claims, ok := parsedToken.Claims.(jwt.MapClaims)
	assert.True(t, ok)
	assert.Equal(t, userID.String(), claims["user_id"])
	assert.Equal(t, role, claims["role"])
	expTime := time.Unix(int64(claims["exp"].(float64)), 0)
	assert.WithinDuration(t, time.Now().Add(ttl), expTime, time.Second)
}