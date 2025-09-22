package comments

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestComment_NewComment(t *testing.T) {
	id := uuid.New()
	text := "Test comment"
	authorID := uuid.New()
	postID := uuid.New()
	now := time.Now()

	comment := Comment{
		ID:        id,
		Text:      text,
		AuthorID:  authorID,
		PostID:    &postID,
		CreatedAt: now,
		UpdatedAt: now,
		Analyzed:  false,
	}

	assert.Equal(t, id, comment.ID)
	assert.Equal(t, text, comment.Text)
	assert.Equal(t, authorID, comment.AuthorID)
	assert.Equal(t, &postID, comment.PostID)
	assert.Equal(t, now, comment.CreatedAt)
	assert.Equal(t, now, comment.UpdatedAt)
	assert.False(t, comment.Analyzed)
}

func TestComment_JSONMarshal(t *testing.T) {
	id := uuid.New()
	comment := Comment{
		ID:        id,
		Text:      "test",
		AuthorID:  uuid.New(),
		PostID:    nil,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		Analyzed:  true,
	}

	data, err := json.Marshal(comment)
	assert.NoError(t, err)

	var unmarshaled Comment
	err = json.Unmarshal(data, &unmarshaled)
	assert.NoError(t, err)

	assert.Equal(t, id, unmarshaled.ID)
	assert.Equal(t, "test", unmarshaled.Text)
	assert.Equal(t, true, unmarshaled.Analyzed)
	assert.Nil(t, unmarshaled.PostID)
}