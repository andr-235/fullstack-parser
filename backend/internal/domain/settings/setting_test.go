package settings

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestSetting_NewSetting(t *testing.T) {
	id := uuid.New()
	key := "test_key"
	value := "test_value"
	description := "test description"
	createdBy := uuid.New()
	now := time.Now()

	setting := Setting{
		ID:          id,
		Key:         key,
		Value:       value,
		Description: description,
		UpdatedAt:   now,
		CreatedBy:   createdBy,
	}

	assert.Equal(t, id, setting.ID)
	assert.Equal(t, key, setting.Key)
	assert.Equal(t, value, setting.Value)
	assert.Equal(t, description, setting.Description)
	assert.Equal(t, now, setting.UpdatedAt)
	assert.Equal(t, createdBy, setting.CreatedBy)
}

func TestSetting_JSONMarshal(t *testing.T) {
	id := uuid.New()
	setting := Setting{
		ID:          id,
		Key:         "key",
		Value:       "value",
		Description: "desc",
		UpdatedAt:   time.Now(),
		CreatedBy:   uuid.New(),
	}

	data, err := json.Marshal(setting)
	assert.NoError(t, err)

	var unmarshaled Setting
	err = json.Unmarshal(data, &unmarshaled)
	assert.NoError(t, err)

	assert.Equal(t, id, unmarshaled.ID)
	assert.Equal(t, "key", unmarshaled.Key)
	assert.Equal(t, "value", unmarshaled.Value)
}