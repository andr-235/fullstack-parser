package comments

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"

	"backend/internal/domain/comments"
	"backend/internal/repository"
	"backend/internal/repository/postgres"
)

// CommentsUseCase - интерфейс для use cases CRUD операций с комментариями.
type CommentsUseCase interface {
	CreateComment(ctx context.Context, text string, authorID uint, postID *uint) (*comments.Comment, error)
	GetComment(ctx context.Context, id uuid.UUID) (*comments.Comment, error)
	UpdateComment(ctx context.Context, id uuid.UUID, text string, currentUserID uint) (*comments.Comment, error)
	DeleteComment(ctx context.Context, id uuid.UUID, currentUserID uint) error
	ListComments(ctx context.Context, filters repository.ListFilters) ([]*comments.Comment, error)
}

// commentsUseCase - реализация use cases для комментариев.
type commentsUseCase struct {
	repo     postgres.CommentRepository
	userRepo postgres.UserRepository // Для проверки автора
	logger   *logrus.Logger
}

// NewCommentsUseCase создает новый экземпляр use cases для комментариев.
func NewCommentsUseCase(repo postgres.CommentRepository, userRepo postgres.UserRepository, logger *logrus.Logger) CommentsUseCase {
	return &commentsUseCase{
		repo:     repo,
		userRepo: userRepo,
		logger:   logger,
	}
}

// CreateComment создает новый комментарий.
// Валидирует текст (длина 1-1000), проверяет автора.
func (uc *commentsUseCase) CreateComment(ctx context.Context, text string, authorID, postID *uuid.UUID) (*comments.Comment, error) {
	if len(text) < 1 || len(text) > 1000 {
		return nil, errors.New("текст комментария должен быть от 1 до 1000 символов")
	}

	// Проверка существования автора
	_, err := uc.userRepo.GetByID(ctx, uint(*authorID))
	if err != nil {
		uc.logger.WithError(err).Error("пользователь не найден при создании комментария")
		return nil, err
	}

	comment := &comments.Comment{
		Text:     text,
		AuthorID: authorID,
		PostID:   postID,
		Analyzed: false,
	}

	err = uc.repo.Create(ctx, comment)
	if err != nil {
		uc.logger.WithError(err).Error("ошибка создания комментария")
		return nil, err
	}

	uc.logger.WithFields(logrus.Fields{
		"comment_id": comment.ID,
		"author_id":  authorID,
	}).Info("комментарий создан успешно")

	return comment, nil
}

// GetComment получает комментарий по ID.
func (uc *commentsUseCase) GetComment(ctx context.Context, id uuid.UUID) (*comments.Comment, error) {
	comment, err := uc.repo.GetByID(ctx, id)
	if err != nil {
		uc.logger.WithError(err).WithField("id", id).Error("комментарий не найден")
		return nil, err
	}

	return comment, nil
}

// UpdateComment обновляет текст комментария.
// Проверяет ownership (author_id == currentUserID), валидация текста.
func (uc *commentsUseCase) UpdateComment(ctx context.Context, id uuid.UUID, text string, currentUserID uuid.UUID) (*comments.Comment, error) {
	if len(text) < 1 || len(text) > 1000 {
		return nil, errors.New("текст комментария должен быть от 1 до 1000 символов")
	}

	comment, err := uc.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}

	if comment.AuthorID != uint(currentUserID) {
		return nil, errors.New("нет прав на обновление комментария")
	}

	comment.Text = text
	comment.UpdatedAt = time.Now()

	err = uc.repo.Update(ctx, comment)
	if err != nil {
		uc.logger.WithError(err).WithField("id", id).Error("ошибка обновления комментария")
		return nil, err
	}

	uc.logger.WithField("id", id).Info("комментарий обновлен успешно")

	return comment, nil
}

// DeleteComment удаляет комментарий.
// Проверяет ownership.
func (uc *commentsUseCase) DeleteComment(ctx context.Context, id uuid.UUID, currentUserID uuid.UUID) error {
	comment, err := uc.repo.GetByID(ctx, id)
	if err != nil {
		return err
	}

	if comment.AuthorID != uint(currentUserID) {
		return errors.New("нет прав на удаление комментария")
	}

	err = uc.repo.Delete(ctx, id)
	if err != nil {
		uc.logger.WithError(err).WithField("id", id).Error("ошибка удаления комментария")
		return err
	}

	uc.logger.WithField("id", id).Info("комментарий удален успешно")

	return nil
}

// ListComments возвращает список комментариев с фильтрами.
func (uc *commentsUseCase) ListComments(ctx context.Context, filters repository.ListFilters) ([]*comments.Comment, error) {
	commentsList, err := uc.repo.List(ctx, filters)
	if err != nil {
		uc.logger.WithError(err).Error("ошибка получения списка комментариев")
		return nil, err
	}

	return commentsList, nil
}