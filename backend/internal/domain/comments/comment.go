package comments

import (
	"time"

	"github.com/google/uuid"
)

// Comment представляет доменную сущность комментария.
// Содержит текст, автора, связь с постом (опционально), временные метки и флаг анализа.
type Comment struct {
	ID        uuid.UUID  `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id" example:"123e4567-e89b-12d3-a456-426614174000"` // Уникальный идентификатор комментария
	Text      string     `gorm:"type:text;not null;size:1000" json:"text" validate:"required,min=1,max=1000"`                              // Текст комментария
	AuthorID  uuid.UUID  `gorm:"type:uuid;not null;index" json:"author_id" validate:"required,uuid"`                                       // ID автора (ссылка на пользователя)
	PostID    *uuid.UUID `gorm:"type:uuid;index" json:"post_id,omitempty" validate:"omitempty,uuid"`                                       // ID поста (опционально, для связи)
	CreatedAt time.Time  `json:"created_at"`                                                                                               // Время создания
	UpdatedAt time.Time  `json:"updated_at"`                                                                                               // Время последнего обновления
	Analyzed  bool       `gorm:"default:false" json:"analyzed"`                                                                            // Флаг, указывающий, был ли проведен анализ ключевых слов
}
