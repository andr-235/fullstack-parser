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

// Константы для валидации
const (
	MinTextLength = 1
	MaxTextLength = 1000
)

// CommentsUseCase - интерфейс для use cases CRUD операций с комментариями.
type CommentsUseCase interface {
	CreateComment(ctx context.Context, text string, authorID uuid.UUID, postID *uuid.UUID) (*comments.Comment, error)
	GetComment(ctx context.Context, id uuid.UUID) (*comments.Comment, error)
	UpdateComment(ctx context.Context, id uuid.UUID, text string, currentUserID uuid.UUID) (*comments.Comment, error)
	DeleteComment(ctx context.Context, id uuid.UUID, currentUserID uuid.UUID) error
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

// validateText проверяет валидность текста комментария.
func (uc *commentsUseCase) validateText(text string) error {
	if len(text) < MinTextLength || len(text) > MaxTextLength {
		return errors.New("текст комментария должен быть от 1 до 1000 символов")
	}
	return nil
}

// checkUserExists проверяет существование пользователя.
func (uc *commentsUseCase) checkUserExists(ctx context.Context, userID uuid.UUID) error {
	_, err := uc.userRepo.GetByID(userID)
	if err != nil {
		uc.logger.WithError(err).WithField("user_id", userID).Error("пользователь не найден")
		return err
	}
	return nil
}

// checkCommentOwnership проверяет права на комментарий.
func (uc *commentsUseCase) checkCommentOwnership(comment *comments.Comment, userID uuid.UUID) error {
	if comment.AuthorID != userID {
		return errors.New("нет прав на выполнение операции с комментарием")
	}
	return nil
}

// logOperation логирует операцию с комментарием.
func (uc *commentsUseCase) logOperation(operation string, commentID uuid.UUID, fields logrus.Fields) {
	uc.logger.WithFields(fields).WithField("comment_id", commentID).Info(operation)
}

// CreateComment создает новый комментарий.
// Валидирует текст (длина 1-1000), проверяет автора.
func (uc *commentsUseCase) CreateComment(ctx context.Context, text string, authorID uuid.UUID, postID *uuid.UUID) (*comments.Comment, error) {
	// Валидация текста
	if err := uc.validateText(text); err != nil {
		return nil, err
	}

	// Проверка существования автора
	if err := uc.checkUserExists(ctx, authorID); err != nil {
		return nil, err
	}

	// Создание комментария
	comment := &comments.Comment{
		Text:     text,
		AuthorID: authorID,
		PostID:   postID,
		Analyzed: false,
	}

	// Сохранение в репозитории
	if err := uc.repo.Create(ctx, comment); err != nil {
		uc.logger.WithError(err).Error("ошибка создания комментария")
		return nil, err
	}

	// Логирование успешного создания
	uc.logOperation("комментарий создан успешно", comment.ID, logrus.Fields{
		"author_id": authorID,
		"post_id":   postID,
	})

	return comment, nil
}

// GetComment получает комментарий по ID.
func (uc *commentsUseCase) GetComment(ctx context.Context, id uuid.UUID) (*comments.Comment, error) {
	comment, err := uc.repo.GetByID(ctx, id)
	if err != nil {
		uc.logger.WithError(err).WithField("comment_id", id).Error("комментарий не найден")
		return nil, err
	}

	return comment, nil
}

// UpdateComment обновляет текст комментария.
// Проверяет ownership (author_id == currentUserID), валидация текста.
func (uc *commentsUseCase) UpdateComment(ctx context.Context, id uuid.UUID, text string, currentUserID uuid.UUID) (*comments.Comment, error) {
	// Валидация текста
	if err := uc.validateText(text); err != nil {
		return nil, err
	}

	// Получение комментария
	comment, err := uc.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}

	// Проверка прав на обновление
	if err := uc.checkCommentOwnership(comment, currentUserID); err != nil {
		return nil, err
	}

	// Обновление данных
	comment.Text = text
	comment.UpdatedAt = time.Now()

	// Сохранение изменений
	if err := uc.repo.Update(ctx, comment); err != nil {
		uc.logger.WithError(err).WithField("comment_id", id).Error("ошибка обновления комментария")
		return nil, err
	}

	// Логирование успешного обновления
	uc.logOperation("комментарий обновлен успешно", id, logrus.Fields{
		"user_id": currentUserID,
	})

	return comment, nil
}

// DeleteComment удаляет комментарий.
// Проверяет ownership.
func (uc *commentsUseCase) DeleteComment(ctx context.Context, id uuid.UUID, currentUserID uuid.UUID) error {
	// Получение комментария
	comment, err := uc.repo.GetByID(ctx, id)
	if err != nil {
		return err
	}

	// Проверка прав на удаление
	if err := uc.checkCommentOwnership(comment, currentUserID); err != nil {
		return err
	}

	// Удаление комментария
	if err := uc.repo.Delete(ctx, id); err != nil {
		uc.logger.WithError(err).WithField("comment_id", id).Error("ошибка удаления комментария")
		return err
	}

	// Логирование успешного удаления
	uc.logOperation("комментарий удален успешно", id, logrus.Fields{
		"user_id": currentUserID,
	})

	return nil
}

// ListComments возвращает список комментариев с фильтрами.
func (uc *commentsUseCase) ListComments(ctx context.Context, filters repository.ListFilters) ([]*comments.Comment, error) {
	commentsList, err := uc.repo.List(ctx, filters)
	if err != nil {
		uc.logger.WithError(err).WithFields(logrus.Fields{
			"filters": filters,
		}).Error("ошибка получения списка комментариев")
		return nil, err
	}

	uc.logger.WithFields(logrus.Fields{
		"count":   len(commentsList),
		"filters": filters,
	}).Debug("список комментариев получен успешно")

	return commentsList, nil
}
