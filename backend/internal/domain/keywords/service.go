// Package keywords определяет доменную модель для ключевых слов.
// service.go содержит доменный сервис для Keyword.

package keywords

import "errors"

// KeywordService - доменный сервис для операций с ключевыми словами.
// Обеспечивает валидацию и активацию в соответствии с бизнес-логикой.
type KeywordService struct{}

// NewKeywordService создает новый экземпляр KeywordService.
func NewKeywordService() *KeywordService {
	return &KeywordService{}
}

// ValidateKeywordText валидирует текст ключевого слова.
// Использует value object для проверки.
func (ks *KeywordService) ValidateKeywordText(text string) error {
	_, err := NewText(text)
	if err != nil {
		return err
	}
	if len(text) < 3 {
		return errors.New("текст должен содержать минимум 3 символа")
	}
	// Placeholder: проверка на запрещенные слова или паттерны.
	return nil
}

// ActivateKeyword активирует ключевое слово через сервис.
// Использует entity метод, добавляет доменную логику если нужно.
func (ks *KeywordService) ActivateKeyword(k *Keyword) error {
	if k == nil {
		return errors.New("ключ не может быть nil")
	}
	k.Activate()
	return nil
}

// DeactivateKeyword деактивирует ключевое слово.
func (ks *KeywordService) DeactivateKeyword(k *Keyword) error {
	if k == nil {
		return errors.New("ключ не может быть nil")
	}
	k.Deactivate()
	return nil
}