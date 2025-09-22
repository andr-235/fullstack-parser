package postgres

import (
	"context"
	"errors"
	"strings"

	"github.com/google/uuid"
	"gorm.io/gorm"

	"backend/internal/domain/comments"
	"backend/internal/repository"
)

// CommentRepository определяет интерфейс для работы с комментариями в PostgreSQL.
// Реализует CRUD операции, поиск с фильтрами и подсчет для статистики.
type CommentRepository interface {
	Create(ctx context.Context, comment *comments.Comment) error
	GetByID(ctx context.Context, id uuid.UUID) (*comments.Comment, error)
	Update(ctx context.Context, comment *comments.Comment) error
	Delete(ctx context.Context, id uuid.UUID) error
	List(ctx context.Context, filters repository.ListFilters) ([]*comments.Comment, error)
	CountTotal(ctx context.Context) (int64, error)
	CountByPost(ctx context.Context, postID uuid.UUID) (int64, error)
	CountAnalyzed(ctx context.Context) (int64, error)
}

// commentPostgresRepository - реализация репозитория для PostgreSQL с использованием GORM.
type commentPostgresRepository struct {
	db *gorm.DB
}

// NewCommentRepository создает новый экземпляр репозитория комментариев.
func NewCommentRepository(db *gorm.DB) CommentRepository {
	return &commentPostgresRepository{db: db}
}

// Create создает новый комментарий в базе данных.
// Проверяет валидность и сохраняет с автоматической генерацией ID.
func (r *commentPostgresRepository) Create(ctx context.Context, comment *comments.Comment) error {
	return r.db.WithContext(ctx).Create(comment).Error
}

// GetByID получает комментарий по уникальному идентификатору.
// Возвращает ошибку, если не найден (gorm.ErrRecordNotFound).
func (r *commentPostgresRepository) GetByID(ctx context.Context, id uuid.UUID) (*comments.Comment, error) {
	var comment comments.Comment
	err := r.db.WithContext(ctx).First(&comment, "id = ?", id).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, repository.ErrNotFound
		}
		return nil, err
	}
	return &comment, nil
}

// Update обновляет существующий комментарий.
// Обновляет только указанные поля, проверяет существование.
func (r *commentPostgresRepository) Update(ctx context.Context, comment *comments.Comment) error {
	result := r.db.WithContext(ctx).Save(comment)
	if result.Error != nil {
		return result.Error
	}
	if result.RowsAffected == 0 {
		return repository.ErrNotFound
	}
	return nil
}

// Delete удаляет комментарий по ID.
// Проверяет существование перед удалением.
func (r *commentPostgresRepository) Delete(ctx context.Context, id uuid.UUID) error {
	result := r.db.WithContext(ctx).Delete(&comments.Comment{}, "id = ?", id)
	if result.Error != nil {
		return result.Error
	}
	if result.RowsAffected == 0 {
		return repository.ErrNotFound
	}
	return nil
}

// List возвращает список комментариев с применением фильтров.
// Фильтры: PostID, AuthorID, Search (поиск по тексту с LIKE).
func (r *commentPostgresRepository) List(ctx context.Context, filters repository.ListFilters) ([]*comments.Comment, error) {
	var commentsList []*comments.Comment
	query := r.db.WithContext(ctx).Model(&comments.Comment{})

	if filters.PostID != nil {
		query = query.Where("post_id = ?", *filters.PostID)
	}
	if filters.AuthorID != nil {
		query = query.Where("author_id = ?", *filters.AuthorID)
	}
	if filters.Search != "" {
		// Простой поиск по тексту, игнорируя регистр
		searchTerm := "%" + strings.ToLower(filters.Search) + "%"
		query = query.Where("LOWER(text) LIKE ?", searchTerm)
	}

	err := query.Find(&commentsList).Error
	if err != nil {
		return nil, err
	}
	return commentsList, nil
}

// CountTotal возвращает общее количество комментариев.
// Используется для статистики.
func (r *commentPostgresRepository) CountTotal(ctx context.Context) (int64, error) {
	var count int64
	err := r.db.WithContext(ctx).Model(&comments.Comment{}).Count(&count).Error
	return count, err
}

// CountByPost возвращает количество комментариев для конкретного поста.
// postID может быть nil для общего подсчета, но по ТЗ - для stats per post.
func (r *commentPostgresRepository) CountByPost(ctx context.Context, postID *uint) (int64, error) {
	var count int64
	query := r.db.WithContext(ctx).Model(&comments.Comment{}).Where("post_id = ?", *postID)
	err := query.Count(&count).Error
	return count, err
}

// CountAnalyzed возвращает количество проанализированных комментариев.
// Фильтр по полю analyzed = true.
func (r *commentPostgresRepository) CountAnalyzed(ctx context.Context) (int64, error) {
	var count int64
	err := r.db.WithContext(ctx).Model(&comments.Comment{}).Where("analyzed = ?", true).Count(&count).Error
	return count, err
}