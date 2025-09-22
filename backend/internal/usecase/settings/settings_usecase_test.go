package settings

import (
	"context"
	"testing"

	"backend/internal/domain/settings"
	"backend/internal/domain/users"
	"backend/internal/repository/postgres"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockSettingRepository struct {
	mock.Mock
	postgres.SettingRepository
}

func (m *MockSettingRepository) List(ctx context.Context) ([]*settings.Setting, error) {
	args := m.Called(ctx)
	return args.Get(0).([]*settings.Setting), args.Error(1)
}

func (m *MockSettingRepository) GetByKey(ctx context.Context, key string) (*settings.Setting, error) {
	args := m.Called(ctx, key)
	return args.Get(0).(*settings.Setting), args.Error(1)
}

func (m *MockSettingRepository) Create(ctx context.Context, setting *settings.Setting) error {
	args := m.Called(ctx, setting)
	return args.Error(0)
}

func (m *MockSettingRepository) Update(ctx context.Context, setting *settings.Setting) error {
	args := m.Called(ctx, setting)
	return args.Error(0)
}

func (m *MockSettingRepository) Delete(ctx context.Context, key string) error {
	args := m.Called(ctx, key)
	return args.Error(0)
}

type MockUserRepository struct {
	mock.Mock
	postgres.UserRepository
}

func (m *MockUserRepository) GetByID(id uuid.UUID) (*users.User, error) {
	args := m.Called(id)
	return args.Get(0).(*users.User), args.Error(1)
}

func TestSettingsUsecase_GetSettings(t *testing.T) {
	mockSettingRepo := new(MockSettingRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil) // Discard logs

	uc := NewSettingsUsecase(mockSettingRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	expectedSettings := []*settings.Setting{{Key: "test"}}
	mockSettingRepo.On("List", ctx).Return(expectedSettings, nil)

	result, err := uc.GetSettings(ctx)

	assert.NoError(t, err)
	assert.Equal(t, expectedSettings, result)

	mockSettingRepo.AssertExpectations(t)
}

func TestSettingsUsecase_GetSettingByKey(t *testing.T) {
	mockSettingRepo := new(MockSettingRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewSettingsUsecase(mockSettingRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	key := "test_key"
	expectedSetting := &settings.Setting{Key: key}
	mockSettingRepo.On("GetByKey", ctx, key).Return(expectedSetting, nil)

	result, err := uc.GetSettingByKey(ctx, key)

	assert.NoError(t, err)
	assert.Equal(t, expectedSetting, result)

	mockSettingRepo.AssertExpectations(t)
}

func TestSettingsUsecase_CreateSetting_Success(t *testing.T) {
	mockSettingRepo := new(MockSettingRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewSettingsUsecase(mockSettingRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	key := "test_key"
	value := "test_value"
	description := "test desc"
	userID := uuid.New()
	user := &users.User{ID: userID, Role: "admin"}
	mockUserRepo.On("GetByID", userID).Return(user, nil)
	mockSettingRepo.On("Create", ctx, mock.AnythingOfType("*settings.Setting")).Return(nil)

	result, err := uc.CreateSetting(ctx, key, value, description, userID)

	assert.NoError(t, err)
	assert.NotNil(t, result)

	mockUserRepo.AssertExpectations(t)
	mockSettingRepo.AssertExpectations(t)
}

func TestSettingsUsecase_CreateSetting_NotAdmin(t *testing.T) {
	mockSettingRepo := new(MockSettingRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewSettingsUsecase(mockSettingRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	key := "test_key"
	value := "test_value"
	description := "test desc"
	userID := uuid.New()
	user := &users.User{ID: userID, Role: "user"}
	mockUserRepo.On("GetByID", userID).Return(user, nil)

	_, err := uc.CreateSetting(ctx, key, value, description, userID)

	assert.Error(t, err)
	assert.Equal(t, "требуется роль admin", err.Error())

	mockUserRepo.AssertExpectations(t)
}

func TestSettingsUsecase_UpdateSetting_Success(t *testing.T) {
	mockSettingRepo := new(MockSettingRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewSettingsUsecase(mockSettingRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	key := "test_key"
	value := "updated_value"
	description := "updated desc"
	userID := uuid.New()
	user := &users.User{ID: userID, Role: "admin"}
	mockUserRepo.On("GetByID", userID).Return(user, nil)
	mockSettingRepo.On("GetByKey", ctx, key).Return(&settings.Setting{Key: key}, nil)
	mockSettingRepo.On("Update", ctx, mock.AnythingOfType("*settings.Setting")).Return(nil)

	result, err := uc.UpdateSetting(ctx, key, value, description, userID)

	assert.NoError(t, err)
	assert.NotNil(t, result)

	mockUserRepo.AssertExpectations(t)
	mockSettingRepo.AssertExpectations(t)
}

func TestSettingsUsecase_DeleteSetting_Success(t *testing.T) {
	mockSettingRepo := new(MockSettingRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewSettingsUsecase(mockSettingRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	key := "test_key"
	userID := uuid.New()
	user := &users.User{ID: userID, Role: "admin"}
	mockUserRepo.On("GetByID", userID).Return(user, nil)
	mockSettingRepo.On("Delete", ctx, key).Return(nil)

	err := uc.DeleteSetting(ctx, key, userID)

	assert.NoError(t, err)

	mockUserRepo.AssertExpectations(t)
	mockSettingRepo.AssertExpectations(t)
}