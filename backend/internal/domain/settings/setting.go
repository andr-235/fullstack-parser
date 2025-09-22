package settings

import (
	"time"

	"github.com/google/uuid"
)

// Setting представляет модель настройки в домене.
type Setting struct {
	ID          uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:gen_random_uuid()"`
	Key         string    `json:"key" gorm:"uniqueIndex;size:255;not null;index"` // Уникальный ключ настройки
	Value       string    `json:"value" gorm:"type:text;not null"`          // Значение настройки (строка или JSON)
	Description string    `json:"description" gorm:"size:500"`              // Описание настройки
	UpdatedAt   time.Time `json:"updated_at" gorm:"autoUpdateTime"`         // Время последнего обновления
	CreatedBy   uuid.UUID `json:"created_by" gorm:"type:uuid;not null"`     // ID пользователя-создателя (FK to users)
}
