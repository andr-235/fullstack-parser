package postgres

import (
	"encoding/json"
	"errors"
	"time"

	"backend/internal/domain/morphological"
	"gorm.io/gorm"
)

// MorphologicalResult представляет модель для хранения результатов анализа в БД.
type MorphologicalResult struct {
	ID        uint   `gorm:"primaryKey"`
	TextHash  string `gorm:"uniqueIndex;not null"`
	Result    string `gorm:"type:jsonb;not null"` // JSONB для AnalysisResult.
	CreatedAt time.Time
}

// MorphologicalRepository - имплементация интерфейса для PostgreSQL.
type MorphologicalRepository struct {
	db *gorm.DB
}

// NewMorphologicalRepository создаёт новый репозиторий для морфологического анализа.
func NewMorphologicalRepository(db *gorm.DB) *MorphologicalRepository {
	return &MorphologicalRepository{db: db}
}

// SaveResult сохраняет результат анализа в БД.
func (r *MorphologicalRepository) SaveResult(textHash string, result *morphological.AnalysisResult) error {
	// Сериализуем result в JSON.
	resultJSON, err := json.Marshal(result)
	if err != nil {
		return errors.New("ошибка сериализации результата")
	}

	morphResult := &MorphologicalResult{
		TextHash: textHash,
		Result:   string(resultJSON),
	}

	if err := r.db.Create(morphResult).Error; err != nil {
		return errors.New("ошибка сохранения результата в БД")
	}

	return nil
}