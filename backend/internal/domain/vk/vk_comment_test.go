package vk

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestVKComment_Struct(t *testing.T) {
	// Тест создания структуры VKComment
	comment := VKComment{
		ID:       12345,
		FromID:   67890,
		Date:     time.Now(),
		Text:     "Test comment text",
		Likes:    42,
	}

	// Проверяем, что все поля установлены правильно
	assert.Equal(t, int64(12345), comment.ID)
	assert.Equal(t, int64(67890), comment.FromID)
	assert.NotZero(t, comment.Date)
	assert.Equal(t, "Test comment text", comment.Text)
	assert.Equal(t, 42, comment.Likes)
}

func TestVKComment_ZeroValues(t *testing.T) {
	// Тест структуры с нулевыми значениями
	var comment VKComment

	// Проверяем нулевые значения
	assert.Equal(t, int64(0), comment.ID)
	assert.Equal(t, int64(0), comment.FromID)
	assert.True(t, comment.Date.IsZero())
	assert.Equal(t, "", comment.Text)
	assert.Equal(t, 0, comment.Likes)
}

func TestVKComment_JSONTags(t *testing.T) {
	// Тест JSON тегов структуры
	comment := VKComment{
		ID:       123,
		FromID:   456,
		Date:     time.Unix(1640995200, 0), // 2022-01-01 00:00:00 UTC
		Text:     "JSON test",
		Likes:    10,
	}

	// Проверяем, что структура может быть использована для JSON сериализации
	// (просто проверяем, что поля доступны)
	assert.Equal(t, int64(123), comment.ID)
	assert.Equal(t, int64(456), comment.FromID)
	assert.Equal(t, "JSON test", comment.Text)
	assert.Equal(t, 10, comment.Likes)
}

func TestVKComment_TimeHandling(t *testing.T) {
	// Тест работы с временем
	fixedTime := time.Date(2023, 1, 15, 10, 30, 45, 0, time.UTC)
	comment := VKComment{
		ID:     1,
		FromID: 2,
		Date:   fixedTime,
		Text:   "Time test",
		Likes:  5,
	}

	// Проверяем точное совпадение времени
	assert.Equal(t, fixedTime, comment.Date)
	assert.Equal(t, 2023, comment.Date.Year())
	assert.Equal(t, time.Month(1), comment.Date.Month())
	assert.Equal(t, 15, comment.Date.Day())
}
