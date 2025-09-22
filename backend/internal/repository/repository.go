package repository

import (
	"errors"

	"github.com/google/uuid"
)

// Общие ошибки репозиториев
var (
	ErrNotFound      = errors.New("entity not found")
	ErrAlreadyExists = errors.New("entity already exists")
	ErrInvalidID     = errors.New("invalid entity ID")
	ErrDatabaseError = errors.New("database error")
)

// ListFilters содержит параметры для фильтрации и пагинации списка сущностей.
type ListFilters struct {
	PostID   *uuid.UUID `json:"post_id,omitempty"`   // Фильтр по ID поста
	AuthorID *uuid.UUID `json:"author_id,omitempty"` // Фильтр по ID автора
	Search   string     `json:"search,omitempty"`    // Поисковый запрос
	Limit    int        `json:"limit,omitempty"`     // Максимальное количество записей
	Offset   int        `json:"offset,omitempty"`    // Смещение для пагинации
}

// PaginationInfo содержит информацию о пагинации.
type PaginationInfo struct {
	Total  int `json:"total"`  // Общее количество записей
	Limit  int `json:"limit"`  // Лимит записей на странице
	Offset int `json:"offset"` // Смещение
	Page   int `json:"page"`   // Текущая страница
}

// Repository - базовый интерфейс для всех репозиториев.
// Определяет общие методы, которые могут быть реализованы в конкретных репозиториях.
type Repository interface {
	// Базовые методы могут быть добавлены здесь при необходимости
	// Например: Exists(ctx context.Context, id uuid.UUID) (bool, error)
}
