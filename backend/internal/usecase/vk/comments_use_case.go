package vk

import (
	"context"
	"fmt"

	"vk-analyzer/internal/domain/comments"
)

// VKCommentsUseCase инкапсулирует бизнес-логику для работы с VK комментариями.
type VKCommentsUseCase struct {
	// Dependencies: VKRepository, AsynqClient, CommentsRepository и т.д. (wired позже)
}

// NewVKCommentsUseCase создает новый экземпляр VKCommentsUseCase.
func NewVKCommentsUseCase() *VKCommentsUseCase {
	return &VKCommentsUseCase{}
}

// FetchComments запускает асинхронную задачу для получения комментариев.
func (uc *VKCommentsUseCase) FetchComments(ctx context.Context, ownerID, postID int) (string, error) {
	// Check if context is cancelled
	select {
	case <-ctx.Done():
		return "", ctx.Err()
	default:
	}

	// Placeholder: в реальности enqueue Asynq task vk:fetch_comments
	taskID := fmt.Sprintf("task_%d_%d", ownerID, postID)
	return taskID, nil
}

// GetCommentsByTaskID получает статус задачи и комментарии.
func (uc *VKCommentsUseCase) GetCommentsByTaskID(ctx context.Context, taskID string) (string, []comments.Comment, error) {
	// Check if context is cancelled
	select {
	case <-ctx.Done():
		return "", nil, ctx.Err()
	default:
	}

	// Placeholder: в реальности check Asynq status, fetch from DB
	var status string
	var commentList []comments.Comment

	// Simulate different statuses based on taskID for testing
	if taskID == "task_pending" {
		status = "pending"
	} else if taskID == "task_failed" {
		status = "failed"
	} else {
		status = "completed"
		commentList = []comments.Comment{{ID: 1, Text: "Mock comment", TaskID: taskID}}
	}

	return status, commentList, nil
}

// ListComments возвращает список комментариев с фильтрацией.
func (uc *VKCommentsUseCase) ListComments(ctx context.Context, taskID string, limit int) ([]comments.Comment, error) {
	// Check if context is cancelled
	select {
	case <-ctx.Done():
		return nil, ctx.Err()
	default:
	}

	// Handle negative limits
	if limit < 0 {
		return []comments.Comment{}, nil
	}

	// Use default limit if 0 is provided
	if limit == 0 {
		limit = 10
	}

	// Placeholder: в реальности query DB with filter
	var commentList []comments.Comment
	for i := 0; i < limit; i++ {
		commentList = append(commentList, comments.Comment{ID: int64(i + 1), Text: fmt.Sprintf("Comment %d", i+1), TaskID: taskID})
	}
	return commentList, nil
}
