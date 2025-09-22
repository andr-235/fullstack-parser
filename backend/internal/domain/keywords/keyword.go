// Package keywords определяет доменную модель для ключевых слов.
package keywords

import (
	"time"

	"github.com/google/uuid"
)

// Keyword представляет доменную сущность ключевого слова.
type Keyword struct {
	ID          uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:gen_random_uuid()"`
	Text        string    `json:"text" gorm:"type:varchar(255);uniqueIndex;not null;index"`
	Active      bool      `json:"active" gorm:"default:true"`
	Description string    `json:"description" gorm:"type:text"`
	CreatedAt   time.Time `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt   time.Time `json:"updated_at" gorm:"autoUpdateTime"`
}

// NewKeyword создает новую сущность Keyword с валидацией.
// Проверяет валидность text с помощью value object.
func NewKeyword(text string, description string) (*Keyword, error) {
	textVO, err := NewText(text)
	if err != nil {
		return nil, err
	}
	// Здесь можно добавить доменную логику, например, проверку на запрещенные символы.
	return &Keyword{
		Text:        textVO.Value(),
		Active:      true,
		Description: description,
	}, nil
}

// Activate активирует ключевое слово.
// Изменяет статус на активный и обновляет время.
func (k *Keyword) Activate() {
	k.Active = true
	k.UpdatedAt = time.Now()
	// Placeholder для domain event: KeywordActivatedEvent.
}

// Deactivate деактивирует ключевое слово.
func (k *Keyword) Deactivate() {
	k.Active = false
	k.UpdatedAt = time.Now()
	// Placeholder для domain event: KeywordDeactivatedEvent.
}

// IsActive возвращает статус активности.
func (k *Keyword) IsActive() bool {
	return k.Active
}
