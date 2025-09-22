// Package users содержит use cases для модуля пользователей.
package users

import (
	"backend/internal/domain/users"
	"backend/internal/repository/postgres"
	"fmt"

	"github.com/go-playground/validator/v10"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

// UserUseCase определяет интерфейс для use cases пользователей.
type UserUseCase interface {
	CreateUser(username, email, password string) (*users.User, error)
	GetUser(id uuid.UUID) (*users.User, error)
	UpdateUser(id uuid.UUID, username, email string) (*users.User, error)
	DeleteUser(id uuid.UUID) error
}

// UserUseCaseImpl реализует UserUseCase.
type UserUseCaseImpl struct {
	repo     postgres.UserRepository
	validate *validator.Validate
}

// NewUserUseCase создает новый экземпляр UserUseCaseImpl.
func NewUserUseCase(repo postgres.UserRepository) UserUseCase {
	return &UserUseCaseImpl{
		repo:     repo,
		validate: validator.New(),
	}
}

// CreateUser создает нового пользователя с хэшированием пароля.
func (uc *UserUseCaseImpl) CreateUser(username, email, password string) (*users.User, error) {
	// Валидация входных данных
	if err := uc.validate.Var(username, "required,min=3,max=255"); err != nil {
		return nil, err
	}
	if err := uc.validate.Var(email, "required,email"); err != nil {
		return nil, err
	}
	if err := uc.validate.Var(password, "required,min=8"); err != nil {
		return nil, err
	}

	// Проверка существования
	if _, err := uc.repo.GetByUsername(username); err == nil {
		return nil, fmt.Errorf("пользователь с username %s уже существует", username)
	}
	if _, err := uc.repo.GetByEmail(email); err == nil {
		return nil, fmt.Errorf("пользователь с email %s уже существует", email)
	}

	// Хэширование пароля
	passwordHash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	user := &users.User{
		Username:     username,
		Email:        email,
		PasswordHash: string(passwordHash),
		Role:         "user",
	}

	if err := uc.repo.Create(user); err != nil {
		return nil, err
	}

	return user, nil
}

// GetUser получает пользователя по ID.
func (uc *UserUseCaseImpl) GetUser(id uuid.UUID) (*users.User, error) {
	user, err := uc.repo.GetByID(id)
	if err != nil {
		return nil, err
	}
	// Не возвращаем PasswordHash
	user.PasswordHash = ""
	return user, nil
}

// UpdateUser обновляет пользователя.
func (uc *UserUseCaseImpl) UpdateUser(id uuid.UUID, username, email string) (*users.User, error) {
	user, err := uc.repo.GetByID(id)
	if err != nil {
		return nil, err
	}

	if username != "" {
		if err := uc.validate.Var(username, "required,min=3,max=255"); err != nil {
			return nil, err
		}
		user.Username = username
	}
	if email != "" {
		if err := uc.validate.Var(email, "required,email"); err != nil {
			return nil, err
		}
		user.Email = email
	}

	if err := uc.repo.Update(user); err != nil {
		return nil, err
	}

	user.PasswordHash = ""
	return user, nil
}

// DeleteUser удаляет пользователя.
func (uc *UserUseCaseImpl) DeleteUser(id uuid.UUID) error {
	return uc.repo.Delete(id)
}
