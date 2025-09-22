package keywords

import (
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestNewKeyword_Success(t *testing.T) {
	text := "test"
	description := "test description"

	keyword, err := NewKeyword(text, description)

	assert.NoError(t, err)
	assert.NotNil(t, keyword)
	assert.Equal(t, text, keyword.Text)
	assert.Equal(t, description, keyword.Description)
	assert.True(t, keyword.Active)
	assert.NotZero(t, keyword.CreatedAt)
	assert.NotZero(t, keyword.UpdatedAt)
}

func TestNewKeyword_InvalidText(t *testing.T) {
	_, err := NewKeyword("", "description")

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "текст не может быть пустым")
}

func TestKeyword_Activate(t *testing.T) {
	id := uuid.New()
	keyword := &Keyword{
		ID:     id,
		Text:   "test",
		Active: false,
	}

	keyword.Activate()

	assert.True(t, keyword.Active)
	assert.WithinDuration(t, time.Now(), keyword.UpdatedAt, time.Second)
}

func TestKeyword_Deactivate(t *testing.T) {
	id := uuid.New()
	keyword := &Keyword{
		ID:     id,
		Text:   "test",
		Active: true,
	}

	keyword.Deactivate()

	assert.False(t, keyword.Active)
	assert.WithinDuration(t, time.Now(), keyword.UpdatedAt, time.Second)
}

func TestKeyword_IsActive(t *testing.T) {
	id := uuid.New()
	activeKeyword := &Keyword{
		ID:     id,
		Text:   "active",
		Active: true,
	}
	inactiveKeyword := &Keyword{
		ID:     id,
		Text:   "inactive",
		Active: false,
	}

	assert.True(t, activeKeyword.IsActive())
	assert.False(t, inactiveKeyword.IsActive())
}