package postgres

import (
	"context"
	"errors"
	"fmt"
	"strings"

	"github.com/google/uuid"
	"gorm.io/gorm"

	"backend/internal/domain/comments"
	"backend/internal/repository"
)

// Константы для запросов
const (
	commentTableName = "comments"
	postIDColumn     = "post_id"
	authorIDColumn   = "author_id"
	textColumn       = "text"
	analyzedColumn   = "analyzed"
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

// buildSearchQuery строит запрос поиска с учетом фильтров.
func (r *commentPostgresRepository) buildSearchQuery(ctx context.Context, filters repository.ListFilters) *gorm.DB {
	query := r.db.WithContext(ctx).Model(&comments.Comment{})

	if filters.PostID != nil {
		query = query.Where(fmt.Sprintf("%s = ?", postIDColumn), *filters.PostID)
	}
	if filters.AuthorID != nil {
		query = query.Where(fmt.Sprintf("%s = ?", authorIDColumn), *filters.AuthorID)
	}
	if filters.Search != "" {
		searchTerm := "%" + strings.ToLower(filters.Search) + "%"
		query = query.Where(fmt.Sprintf("LOWER(%s) LIKE ?", textColumn), searchTerm)
	}

	// Применяем пагинацию
	if filters.Limit > 0 {
		query = query.Limit(filters.Limit)
	}
	if filters.Offset > 0 {
		query = query.Offset(filters.Offset)
	}

	return query
}

// handleGormError обрабатывает ошибки GORM и преобразует их в стандартные ошибки репозитория.
func (r *commentPostgresRepository) handleGormError(err error) error {
	if err == nil {
		return nil
	}
	if errors.Is(err, gorm.ErrRecordNotFound) {
		return repository.ErrNotFound
	}
	return err
}

// Create создает новый комментарий в базе данных.
// Проверяет валидность и сохраняет с автоматической генерацией ID.
func (r *commentPostgresRepository) Create(ctx context.Context, comment *comments.Comment) error {
	if comment == nil {
		return repository.ErrInvalidID
	}
	return r.handleGormError(r.db.WithContext(ctx).Create(comment).Error)
}

// GetByID получает комментарий по уникальному идентификатору.
// Возвращает ошибку, если не найден (gorm.ErrRecordNotFound).
func (r *commentPostgresRepository) GetByID(ctx context.Context, id uuid.UUID) (*comments.Comment, error) {
	if id == uuid.Nil {
		return nil, repository.ErrInvalidID
	}

	var comment comments.Comment
	err := r.db.WithContext(ctx).First(&comment, "id = ?", id).Error
	if err != nil {
		return nil, r.handleGormError(err)
	}
	return &comment, nil
}

// Update обновляет существующий комментарий.
// Обновляет только указанные поля, проверяет существование.
func (r *commentPostgresRepository) Update(ctx context.Context, comment *comments.Comment) error {
	if comment == nil || comment.ID == uuid.Nil {
		return repository.ErrInvalidID
	}

	result := r.db.WithContext(ctx).Save(comment)
	if result.Error != nil {
		return r.handleGormError(result.Error)
	}
	if result.RowsAffected == 0 {
		return repository.ErrNotFound
	}
	return nil
}

// Delete удаляет комментарий по ID.
// Проверяет существование перед удалением.
func (r *commentPostgresRepository) Delete(ctx context.Context, id uuid.UUID) error {
	if id == uuid.Nil {
		return repository.ErrInvalidID
	}

	result := r.db.WithContext(ctx).Delete(&comments.Comment{}, "id = ?", id)
	if result.Error != nil {
		return r.handleGormError(result.Error)
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
	query := r.buildSearchQuery(ctx, filters)

	err := query.Find(&commentsList).Error
	if err != nil {
		return nil, r.handleGormError(err)
	}
	return commentsList, nil
}

// CountTotal возвращает общее количество комментариев.
// Используется для статистики.
func (r *commentPostgresRepository) CountTotal(ctx context.Context) (int64, error) {
	var count int64
	err := r.db.WithContext(ctx).Model(&comments.Comment{}).Count(&count).Error
	return count, r.handleGormError(err)
}

// CountByPost возвращает количество комментариев для конкретного поста.
func (r *commentPostgresRepository) CountByPost(ctx context.Context, postID uuid.UUID) (int64, error) {
	if postID == uuid.Nil {
		return 0, repository.ErrInvalidID
	}

	var count int64
	query := r.db.WithContext(ctx).Model(&comments.Comment{}).Where(fmt.Sprintf("%s = ?", postIDColumn), postID)
	err := query.Count(&count).Error
	return count, r.handleGormError(err)
}

// CountAnalyzed возвращает количество проанализированных комментариев.
// Фильтр по полю analyzed = true.
func (r *commentPostgresRepository) CountAnalyzed(ctx context.Context) (int64, error) {
	var count int64
	err := r.db.WithContext(ctx).Model(&comments.Comment{}).Where(fmt.Sprintf("%s = ?", analyzedColumn), true).Count(&count).Error
	return count, r.handleGormError(err)
}
