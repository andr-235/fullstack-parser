package tasks

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestTask_NewTask(t *testing.T) {
	id := "task-id"
	taskType := "analyze_comment"
	payload := []byte(`{"comment_id": "123"}`)
	status := StatusPending
	now := time.Now()

	task := Task{
		ID:        id,
		Type:      taskType,
		Payload:   payload,
		Status:    status,
		CreatedAt: now,
	}

	assert.Equal(t, id, task.ID)
	assert.Equal(t, taskType, task.Type)
	assert.Equal(t, payload, task.Payload)
	assert.Equal(t, status, task.Status)
	assert.Equal(t, now, task.CreatedAt)
	assert.Empty(t, task.Result)
	assert.Empty(t, task.Error)
}

func TestTask_JSONMarshal(t *testing.T) {
	task := Task{
		ID:        "id",
		Type:      "type",
		Payload:   []byte(`{"key": "value"}`),
		Status:    StatusCompleted,
		Result:    []byte(`{"success": true}`),
		Error:     "",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	data, err := json.Marshal(task)
	assert.NoError(t, err)

	var unmarshaled Task
	err = json.Unmarshal(data, &unmarshaled)
	assert.NoError(t, err)

	assert.Equal(t, "id", unmarshaled.ID)
	assert.Equal(t, "type", unmarshaled.Type)
	assert.Equal(t, StatusCompleted, unmarshaled.Status)
	assert.Equal(t, []byte(`{"success": true}`), unmarshaled.Result)
}

func TestStatus_ValidStatuses(t *testing.T) {
	validStatuses := []Status{StatusPending, StatusActive, StatusCompleted, StatusFailed, StatusCanceled}

	for _, status := range validStatuses {
		assert.NotEmpty(t, status)
	}
}