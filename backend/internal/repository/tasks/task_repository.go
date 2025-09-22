package tasks

import (
	"context"
	"errors"
)

type TaskRepository interface {
	SetStatus(ctx context.Context, taskID string, status string, result interface{}) error
	GetStatus(ctx context.Context, taskID string) (string, interface{}, error)
	GetTaskResults(ctx context.Context, taskID string) (interface{}, error)
}

// Status constants
const (
	StatusPending    = "pending"
	StatusProcessing = "processing"
	StatusCompleted  = "completed"
	StatusFailed     = "failed"
)

// ErrTaskNotFound for missing tasks
var ErrTaskNotFound = errors.New("task not found")