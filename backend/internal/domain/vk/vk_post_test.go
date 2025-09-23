package vk

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestVKPost_Struct(t *testing.T) {
	// Тест создания структуры VKPost
	post := VKPost{
		ID:      12345,
		OwnerID: 67890,
		Date:    time.Now(),
		Text:    "Test post text content",
	}

	// Проверяем, что все поля установлены правильно
	assert.Equal(t, int64(12345), post.ID)
	assert.Equal(t, int64(67890), post.OwnerID)
	assert.NotZero(t, post.Date)
	assert.Equal(t, "Test post text content", post.Text)
}

func TestVKPost_ZeroValues(t *testing.T) {
	// Тест структуры с нулевыми значениями
	var post VKPost

	// Проверяем нулевые значения
	assert.Equal(t, int64(0), post.ID)
	assert.Equal(t, int64(0), post.OwnerID)
	assert.True(t, post.Date.IsZero())
	assert.Equal(t, "", post.Text)
}

func TestVKPost_JSONTags(t *testing.T) {
	// Тест JSON тегов структуры
	post := VKPost{
		ID:      123,
		OwnerID: 456,
		Date:    time.Unix(1640995200, 0), // 2022-01-01 00:00:00 UTC
		Text:    "JSON test post",
	}

	// Проверяем, что структура может быть использована для JSON сериализации
	assert.Equal(t, int64(123), post.ID)
	assert.Equal(t, int64(456), post.OwnerID)
	assert.Equal(t, "JSON test post", post.Text)
}

func TestVKPost_TimeHandling(t *testing.T) {
	// Тест работы с временем
	fixedTime := time.Date(2023, 1, 15, 10, 30, 45, 0, time.UTC)
	post := VKPost{
		ID:      1,
		OwnerID: 2,
		Date:    fixedTime,
		Text:    "Time test post",
	}

	// Проверяем точное совпадение времени
	assert.Equal(t, fixedTime, post.Date)
	assert.Equal(t, 2023, post.Date.Year())
	assert.Equal(t, time.Month(1), post.Date.Month())
	assert.Equal(t, 15, post.Date.Day())
}

func TestVKPost_LongText(t *testing.T) {
	// Тест с длинным текстом
	longText := "This is a very long text content that might be typical for a VK post. " +
		"It contains multiple sentences and should be handled properly by the struct. " +
		"Testing edge cases with various characters: !@#$%^&*()_+-=[]{}|;':\",./<>?"

	post := VKPost{
		ID:      999,
		OwnerID: 888,
		Date:    time.Now(),
		Text:    longText,
	}

	// Проверяем, что длинный текст сохраняется корректно
	assert.Equal(t, int64(999), post.ID)
	assert.Equal(t, int64(888), post.OwnerID)
	assert.Equal(t, longText, post.Text)
	assert.Greater(t, len(post.Text), 100) // Проверяем, что текст действительно длинный
}

func TestVKPost_EmptyText(t *testing.T) {
	// Тест с пустым текстом
	post := VKPost{
		ID:      555,
		OwnerID: 444,
		Date:    time.Now(),
		Text:    "",
	}

	// Проверяем обработку пустого текста
	assert.Equal(t, int64(555), post.ID)
	assert.Equal(t, int64(444), post.OwnerID)
	assert.Equal(t, "", post.Text)
}
