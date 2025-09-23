package vk

import (
	"context"
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestFetchComments_Success(t *testing.T) {
	// Arrange
	uc := NewVKCommentsUseCase()
	ctx := context.Background()

	// Act
	taskID, err := uc.FetchComments(ctx, -123, 456)

	// Assert
	assert.NoError(t, err)
	assert.NotEmpty(t, taskID)
	assert.Contains(t, taskID, "task_-123_456")
}

func TestFetchComments_ContextCanceled(t *testing.T) {
	// Arrange
	uc := NewVKCommentsUseCase()
	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	// Act
	taskID, err := uc.FetchComments(ctx, -123, 456)

	// Assert
	assert.Error(t, err)
	assert.Empty(t, taskID)
	assert.Equal(t, context.Canceled, err)
}

func TestGetCommentsByTaskID_Completed(t *testing.T) {
	// Arrange
	uc := NewVKCommentsUseCase()
	ctx := context.Background()
	taskID := "test_task"

	// Act
	status, comments, err := uc.GetCommentsByTaskID(ctx, taskID)

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, "completed", status)
	assert.Len(t, comments, 1)
	assert.Equal(t, int64(1), comments[0].ID)
	assert.Equal(t, "Mock comment", comments[0].Text)
	assert.Equal(t, taskID, comments[0].TaskID)
}

func TestGetCommentsByTaskID_EmptyTaskID(t *testing.T) {
	// Arrange
	uc := NewVKCommentsUseCase()
	ctx := context.Background()

	// Act
	status, comments, err := uc.GetCommentsByTaskID(ctx, "")

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, "completed", status) // Placeholder behavior
	assert.Len(t, comments, 1)
	assert.Equal(t, int64(1), comments[0].ID)
	assert.Empty(t, comments[0].TaskID)
}

func TestListComments_WithLimit(t *testing.T) {
	// Arrange
	uc := NewVKCommentsUseCase()
	ctx := context.Background()
	taskID := "test_task"
	limit := 3

	// Act
	comments, err := uc.ListComments(ctx, taskID, limit)

	// Assert
	assert.NoError(t, err)
	assert.Len(t, comments, 3)
	for i, comment := range comments {
		assert.Equal(t, int64(i+1), comment.ID)
		assert.Equal(t, fmt.Sprintf("Comment %d", i+1), comment.Text)
		assert.Equal(t, taskID, comment.TaskID)
	}
}

func TestListComments_DefaultLimit(t *testing.T) {
	// Arrange
	uc := NewVKCommentsUseCase()
	ctx := context.Background()
	taskID := ""

	// Act
	comments, err := uc.ListComments(ctx, taskID, 0) // 0 should use default

	// Assert
	assert.NoError(t, err)
	assert.Len(t, comments, 10) // Default limit in handler is 10, but use case uses limit
}

func TestListComments_ZeroLimit(t *testing.T) {
	// Arrange
	uc := NewVKCommentsUseCase()
	ctx := context.Background()
	taskID := "test_task"

	// Act
	comments, err := uc.ListComments(ctx, taskID, -1) // Use negative limit to get empty result

	// Assert
	assert.NoError(t, err)
	assert.Len(t, comments, 0) // Should return empty list for negative limit
}

func TestListComments_ContextTimeout(t *testing.T) {
	// Arrange
	uc := NewVKCommentsUseCase()
	ctx, cancel := context.WithTimeout(context.Background(), 0)
	defer cancel()

	// Act
	comments, err := uc.ListComments(ctx, "test_task", 5)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, comments)
	assert.Equal(t, context.DeadlineExceeded, err)
}
