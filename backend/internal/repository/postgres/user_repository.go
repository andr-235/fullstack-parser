// Package postgres содержит реализации репозиториев для PostgreSQL.
package postgres

import (
	"internal/domain/users"

	"gorm.io/gorm"
)

// UserRepository определяет интерфейс для работы с пользователями в БД.
type UserRepository interface {
	Create(user *users.User) error
	GetByID(id uint) (*users.User, error)
	GetByEmail(email string) (*users.User, error)
	GetByUsername(username string) (*users.User, error)
	Update(user *users.User) error
	Delete(id uint) error
}

// UserRepositoryImpl реализует UserRepository с использованием GORM.
type UserRepositoryImpl struct {
	db *gorm.DB
}

// NewUserRepository создает новый экземпляр UserRepositoryImpl.
func NewUserRepository(db *gorm.DB) UserRepository {
	return &UserRepositoryImpl{db: db}
}

// Create создает нового пользователя в БД.
func (r *UserRepositoryImpl) Create(user *users.User) error {
	return r.db.Create(user).Error
}

// GetByID получает пользователя по ID.
func (r *UserRepositoryImpl) GetByID(id uint) (*users.User, error) {
	var user users.User
	err := r.db.First(&user, id).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// GetByEmail получает пользователя по email.
func (r *UserRepositoryImpl) GetByEmail(email string) (*users.User, error) {
	var user users.User
	err := r.db.Where("email = ?", email).First(&user).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// GetByUsername получает пользователя по username.
func (r *UserRepositoryImpl) GetByUsername(username string) (*users.User, error) {
	var user users.User
	err := r.db.Where("username = ?", username).First(&user).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// Update обновляет пользователя в БД.
func (r *UserRepositoryImpl) Update(user *users.User) error {
	return r.db.Save(user).Error
}

// Delete удаляет пользователя по ID.
func (r *UserRepositoryImpl) Delete(id uint) error {
	return r.db.Delete(&users.User{}, id).Error
}