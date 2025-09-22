package morphological

import "backend/internal/domain"

// TextAnalysis represents the result of morphological analysis of text.
type TextAnalysis struct {
	Keywords []string                 `json:"keywords" gorm:"type:json"`
	Tone     string                   `json:"tone"`
	Entities map[string][]string       `json:"entities" gorm:"type:json"`
	Score    float64                  `json:"score"`
}