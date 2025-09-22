package settings

import "time"

// Setting представляет модель настройки в домене.
type Setting struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	Key         string    `json:"key" gorm:"uniqueIndex;size:255;not null"` // Уникальный ключ настройки
	Value       string    `json:"value" gorm:"type:text;not null"`          // Значение настройки (строка или JSON)
	Description string    `json:"description" gorm:"size:500"`              // Описание настройки
	UpdatedAt   time.Time `json:"updated_at" gorm:"autoUpdateTime"`         // Время последнего обновления
	CreatedBy   uint      `json:"created_by" gorm:"not null"`               // ID пользователя-создателя (FK to users)
}