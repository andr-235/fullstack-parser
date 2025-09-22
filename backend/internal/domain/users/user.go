// Package users содержит доменные сущности для модуля пользователей.
package users

import "time"

// User представляет сущность пользователя в доменной модели.
type User struct {
	ID            uint      `json:"id" gorm:"primaryKey"`
	Username      string    `json:"username" gorm:"uniqueIndex;not null;size:255"`
	Email         string    `json:"email" gorm:"uniqueIndex;not null;size:255"`
	PasswordHash  string    `json:"-" gorm:"not null;size:255"` // Пароль не экспортируется в JSON
	Role          string    `json:"role" gorm:"default:user;size:50"` // Роли: user, admin
	CreatedAt     time.Time `json:"created_at"`
	UpdatedAt     time.Time `json:"updated_at"`
}