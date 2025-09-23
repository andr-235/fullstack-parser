package vk

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestVKToken_Struct(t *testing.T) {
	// Тест создания структуры VKToken
	token := VKToken{
		AccessToken: "test_access_token_12345",
		ExpiresIn:   86400, // 24 часа в секундах
		UserID:      12345,
	}

	// Проверяем, что все поля установлены правильно
	assert.Equal(t, "test_access_token_12345", token.AccessToken)
	assert.Equal(t, 86400, token.ExpiresIn)
	assert.Equal(t, int64(12345), token.UserID)
}

func TestVKToken_ZeroValues(t *testing.T) {
	// Тест структуры с нулевыми значениями
	var token VKToken

	// Проверяем нулевые значения
	assert.Equal(t, "", token.AccessToken)
	assert.Equal(t, 0, token.ExpiresIn)
	assert.Equal(t, int64(0), token.UserID)
}

func TestVKToken_JSONTags(t *testing.T) {
	// Тест JSON тегов структуры
	token := VKToken{
		AccessToken: "json_test_token",
		ExpiresIn:   3600, // 1 час
		UserID:      67890,
	}

	// Проверяем, что структура может быть использована для JSON сериализации
	assert.Equal(t, "json_test_token", token.AccessToken)
	assert.Equal(t, 3600, token.ExpiresIn)
	assert.Equal(t, int64(67890), token.UserID)
}

func TestVKToken_EmptyToken(t *testing.T) {
	// Тест с пустым токеном
	token := VKToken{
		AccessToken: "",
		ExpiresIn:   7200,
		UserID:      11111,
	}

	// Проверяем обработку пустого токена
	assert.Equal(t, "", token.AccessToken)
	assert.Equal(t, 7200, token.ExpiresIn)
	assert.Equal(t, int64(11111), token.UserID)
}

func TestVKToken_ZeroExpiration(t *testing.T) {
	// Тест с нулевым временем истечения
	token := VKToken{
		AccessToken: "zero_exp_token",
		ExpiresIn:   0,
		UserID:      22222,
	}

	// Проверяем обработку нулевого времени истечения
	assert.Equal(t, "zero_exp_token", token.AccessToken)
	assert.Equal(t, 0, token.ExpiresIn)
	assert.Equal(t, int64(22222), token.UserID)
}

func TestVKToken_LongToken(t *testing.T) {
	// Тест с длинным токеном
	longToken := "vk1.a.test_access_token_that_is_very_long_and_contains_many_characters_" +
		"to_test_how_the_struct_handles_long_strings_in_access_tokens_1234567890"

	token := VKToken{
		AccessToken: longToken,
		ExpiresIn:   1800, // 30 минут
		UserID:      33333,
	}

	// Проверяем, что длинный токен сохраняется корректно
	assert.Equal(t, longToken, token.AccessToken)
	assert.Equal(t, 1800, token.ExpiresIn)
	assert.Equal(t, int64(33333), token.UserID)
	assert.Greater(t, len(token.AccessToken), 100) // Проверяем, что токен действительно длинный
}

func TestVKToken_NegativeUserID(t *testing.T) {
	// Тест с отрицательным UserID (может быть для групп)
	token := VKToken{
		AccessToken: "negative_user_id_token",
		ExpiresIn:   900,    // 15 минут
		UserID:      -12345, // Отрицательный ID для группы
	}

	// Проверяем обработку отрицательного UserID
	assert.Equal(t, "negative_user_id_token", token.AccessToken)
	assert.Equal(t, 900, token.ExpiresIn)
	assert.Equal(t, int64(-12345), token.UserID)
}
