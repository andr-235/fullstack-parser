package comments

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestComment_Struct(t *testing.T) {
	// Тест создания основной структуры Comment
	comment := Comment{
		ID:             12345,
		FromID:         67890,
		Date:           1640995200, // 2022-01-01 00:00:00 UTC
		Text:           "Test comment text",
		Keywords:       []string{"test", "comment"},
		Sentiment:      "positive",
	}

	// Проверяем, что все поля установлены правильно
	assert.Equal(t, int64(12345), comment.ID)
	assert.Equal(t, int64(67890), comment.FromID)
	assert.Equal(t, int64(1640995200), comment.Date)
	assert.Equal(t, "Test comment text", comment.Text)
	assert.Equal(t, []string{"test", "comment"}, comment.Keywords)
	assert.Equal(t, "positive", comment.Sentiment)
}

func TestComment_ZeroValues(t *testing.T) {
	// Тест структуры с нулевыми значениями
	var comment Comment

	// Проверяем нулевые значения
	assert.Equal(t, int64(0), comment.ID)
	assert.Equal(t, int64(0), comment.FromID)
	assert.Equal(t, int64(0), comment.Date)
	assert.Equal(t, "", comment.Text)
	assert.Nil(t, comment.Donut)
	assert.Nil(t, comment.ReplyToUser)
	assert.Nil(t, comment.ReplyToComment)
	assert.Nil(t, comment.Attachments)
	assert.Nil(t, comment.ParentsStack)
	assert.Nil(t, comment.Thread)
	assert.Nil(t, comment.Likes)
	assert.Nil(t, comment.Keywords)
	assert.Equal(t, "", comment.Sentiment)
}

func TestComment_JSONTags(t *testing.T) {
	// Тест JSON тегов структуры
	comment := Comment{
		ID:     123,
		FromID: 456,
		Date:   1640995200,
		Text:   "JSON test comment",
	}

	// Проверяем, что структура может быть использована для JSON сериализации
	assert.Equal(t, int64(123), comment.ID)
	assert.Equal(t, int64(456), comment.FromID)
	assert.Equal(t, int64(1640995200), comment.Date)
	assert.Equal(t, "JSON test comment", comment.Text)
}

func TestComment_WithDonut(t *testing.T) {
	// Тест с Donut информацией
	donut := &Donut{
		IsDon:       true,
		Placeholder: "Donut content",
	}

	comment := Comment{
		ID:     111,
		FromID: 222,
		Date:   1640995200,
		Text:   "Comment with donut",
		Donut:  donut,
	}

	// Проверяем Donut поля
	assert.NotNil(t, comment.Donut)
	assert.True(t, comment.Donut.IsDon)
	assert.Equal(t, "Donut content", comment.Donut.Placeholder)
}

func TestComment_WithLikes(t *testing.T) {
	// Тест с информацией о лайках
	likes := &Likes{
		Count:     42,
		UserLikes: 1,
		CanLike:   1,
	}

	comment := Comment{
		ID:     333,
		FromID: 444,
		Date:   1640995200,
		Text:   "Comment with likes",
		Likes:  likes,
	}

	// Проверяем Likes поля
	assert.NotNil(t, comment.Likes)
	assert.Equal(t, 42, comment.Likes.Count)
	assert.Equal(t, 1, comment.Likes.UserLikes)
	assert.Equal(t, 1, comment.Likes.CanLike)
}

func TestComment_WithThread(t *testing.T) {
	// Тест с вложенными комментариями
	thread := &Thread{
		Count:           5,
		CanPost:         true,
		ShowReplyButton: true,
		GroupsCanPost:   false,
	}

	comment := Comment{
		ID:     555,
		FromID: 666,
		Date:   1640995200,
		Text:   "Comment with thread",
		Thread: thread,
	}

	// Проверяем Thread поля
	assert.NotNil(t, comment.Thread)
	assert.Equal(t, 5, comment.Thread.Count)
	assert.True(t, comment.Thread.CanPost)
	assert.True(t, comment.Thread.ShowReplyButton)
	assert.False(t, comment.Thread.GroupsCanPost)
}

func TestComment_WithReplyTo(t *testing.T) {
	// Тест с информацией об ответе
	replyToUser := int64(12345)
	replyToComment := int64(67890)

	comment := Comment{
		ID:             777,
		FromID:         888,
		Date:           1640995200,
		Text:           "Reply comment",
		ReplyToUser:    &replyToUser,
		ReplyToComment: &replyToComment,
	}

	// Проверяем ReplyTo поля
	assert.NotNil(t, comment.ReplyToUser)
	assert.NotNil(t, comment.ReplyToComment)
	assert.Equal(t, int64(12345), *comment.ReplyToUser)
	assert.Equal(t, int64(67890), *comment.ReplyToComment)
}

func TestComment_WithParentsStack(t *testing.T) {
	// Тест с цепочкой родителей
	parentsStack := []int64{11111, 22222, 33333}

	comment := Comment{
		ID:           999,
		FromID:       1000,
		Date:         1640995200,
		Text:         "Nested comment",
		ParentsStack: parentsStack,
	}

	// Проверяем ParentsStack
	assert.NotNil(t, comment.ParentsStack)
	assert.Len(t, comment.ParentsStack, 3)
	assert.Equal(t, []int64{11111, 22222, 33333}, comment.ParentsStack)
}

func TestComment_WithAttachments(t *testing.T) {
	// Тест с вложениями (пустой массив)
	attachments := []interface{}{}

	comment := Comment{
		ID:          1111,
		FromID:      2222,
		Date:        1640995200,
		Text:        "Comment with attachments",
		Attachments: attachments,
	}

	// Проверяем Attachments
	assert.NotNil(t, comment.Attachments)
	assert.Len(t, comment.Attachments, 0)
}

func TestComment_ComplexScenario(t *testing.T) {
	// Тест комплексного сценария с множественными вложенными структурами
	donut := &Donut{
		IsDon:       true,
		Placeholder: "Premium content",
	}

	likes := &Likes{
		Count:     15,
		UserLikes: 1,
		CanLike:   1,
	}

	thread := &Thread{
		Count:           3,
		CanPost:         true,
		ShowReplyButton: true,
		GroupsCanPost:   true,
	}

	replyToUser := int64(99999)

	comment := Comment{
		ID:             12345,
		FromID:         67890,
		Date:           1640995200,
		Text:           "Complex comment with all features",
		Donut:          donut,
		Likes:          likes,
		Thread:         thread,
		ReplyToUser:    &replyToUser,
		Keywords:       []string{"complex", "test", "features"},
		Sentiment:      "neutral",
	}

	// Проверяем все поля комплексного комментария
	assert.Equal(t, int64(12345), comment.ID)
	assert.Equal(t, int64(67890), comment.FromID)
	assert.Equal(t, int64(1640995200), comment.Date)
	assert.Equal(t, "Complex comment with all features", comment.Text)
	assert.NotNil(t, comment.Donut)
	assert.True(t, comment.Donut.IsDon)
	assert.Equal(t, "Premium content", comment.Donut.Placeholder)
	assert.NotNil(t, comment.Likes)
	assert.Equal(t, 15, comment.Likes.Count)
	assert.NotNil(t, comment.Thread)
	assert.Equal(t, 3, comment.Thread.Count)
	assert.NotNil(t, comment.ReplyToUser)
	assert.Equal(t, int64(99999), *comment.ReplyToUser)
	assert.Equal(t, []string{"complex", "test", "features"}, comment.Keywords)
	assert.Equal(t, "neutral", comment.Sentiment)
}
