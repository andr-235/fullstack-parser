// Package keywords определяет доменную модель для ключевых слов.
// value_objects.go содержит value objects для Keyword.

package keywords

import "errors"

// Text представляет значение ключевого слова с валидацией.
type Text struct {
	value string
}

// NewText создает новый Text с проверкой валидности.
// Текст не должен быть пустым и превышать 255 символов.
func NewText(value string) (*Text, error) {
	if len(value) == 0 {
		return nil, errors.New("текст не может быть пустым")
	}
	if len(value) > 255 {
		return nil, errors.New("текст не может превышать 255 символов")
	}
	return &Text{value: value}, nil
}

// Value возвращает строковое значение Text.
func (t *Text) Value() string {
	return t.value
}

// ActiveStatus представляет статус активности ключевого слова.
type ActiveStatus bool

// NewActiveStatus создает новый ActiveStatus.
func NewActiveStatus(active bool) ActiveStatus {
	return ActiveStatus(active)
}

// IsActive проверяет, активен ли статус.
func (as ActiveStatus) IsActive() bool {
	return bool(as)
}