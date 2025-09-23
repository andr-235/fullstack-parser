package vk

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestVKCommentMarshalJSON(t *testing.T) {
	// Arrange
	comment := VKComment{
		ID:     1,
		FromID: 123,
		Date:   time.Unix(1234567890, 0),
		Text:   "Test comment",
		Likes:  5,
	}

	// Act
	jsonData, err := json.Marshal(comment)

	// Assert
	assert.NoError(t, err)

	// Проверяем отдельные поля, так как time.Time сериализуется как строка
	var result map[string]interface{}
	err = json.Unmarshal(jsonData, &result)
	assert.NoError(t, err)

	assert.Equal(t, float64(1), result["id"])
	assert.Equal(t, float64(123), result["from_id"])
	assert.Equal(t, "Test comment", result["text"])
	assert.Equal(t, float64(5), result["likes_count"])

	// Проверяем, что date является строкой времени
	dateStr, ok := result["date"].(string)
	assert.True(t, ok)
	assert.NotEmpty(t, dateStr)
}

func TestVKCommentUnmarshalJSON(t *testing.T) {
	// Arrange
	jsonData := []byte(`{"id":1,"from_id":123,"date":"2009-02-14T09:31:30+10:00","text":"Test comment","likes_count":5}`)

	// Act
	var comment VKComment
	err := json.Unmarshal(jsonData, &comment)

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, int64(1), comment.ID)
	assert.Equal(t, int64(123), comment.FromID)
	assert.Equal(t, "Test comment", comment.Text)
	assert.Equal(t, 5, comment.Likes)

	// Проверяем, что дата была корректно распарсена
	expectedTime := time.Date(2009, time.February, 14, 9, 31, 30, 0, time.FixedZone("+10", 10*3600))
	assert.Equal(t, expectedTime.Unix(), comment.Date.Unix())
}

func TestVKCommentInvalidJSON(t *testing.T) {
	// Arrange
	invalidJSON := []byte(`{"id":1,"from_id":"invalid","date":"invalid","text":"","likes_count":"invalid"}`)

	// Act
	var comment VKComment
	err := json.Unmarshal(invalidJSON, &comment)

	// Assert
	assert.Error(t, err)
}

func TestVKCommentEmptyText(t *testing.T) {
	// Arrange
	comment := VKComment{
		ID:     1,
		FromID: 123,
		Date:   time.Unix(1234567890, 0),
		Text:   "",
		Likes:  0,
	}

	// Act
	jsonData, err := json.Marshal(comment)

	// Assert
	assert.NoError(t, err)
	assert.Contains(t, string(jsonData), `"text":""`)
}

func TestVKCommentZeroValues(t *testing.T) {
	// Arrange
	var comment VKComment

	// Act
	jsonData, err := json.Marshal(comment)

	// Assert
	assert.NoError(t, err)
	assert.Contains(t, string(jsonData), `"id":0`)
	assert.Contains(t, string(jsonData), `"from_id":0`)
	assert.Contains(t, string(jsonData), `"text":""`)
	assert.Contains(t, string(jsonData), `"likes_count":0`)
}
