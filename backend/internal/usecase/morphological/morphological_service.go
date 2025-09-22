package morphological

import (
	"errors"
	"strings"

	"backend/internal/domain/morphological"
)

// MorphologyService определяет интерфейс для морфологического анализа текста.
type MorphologyService interface {
	AnalyzeText(text string) (*morphological.AnalysisResult, error)
}

// PlaceholderMorphologyService - простая реализация сервиса анализа с placeholder логикой.
type PlaceholderMorphologyService struct{}

// NewMorphologyService создаёт новый экземпляр сервиса морфологии (placeholder).
func NewMorphologyService() MorphologyService {
	return &PlaceholderMorphologyService{}
}

// AnalyzeText выполняет placeholder анализ: разбивает текст на слова, леммы - слова в нижнем регистре, POS - "NOUN" для всех.
func (s *PlaceholderMorphologyService) AnalyzeText(text string) (*morphological.AnalysisResult, error) {
	if text == "" {
		return nil, errors.New("текст не может быть пустым")
	}

	// Разбиваем текст на слова, удаляем пунктуацию и приводим к нижнему регистру.
	words := strings.Fields(strings.ToLower(text))
	// Удаляем неалфавитные символы из слов (простой placeholder).
	var cleanWords []string
	for _, word := range words {
		cleanWord := strings.Trim(word, ".,!?;:'\"-()[]{}")
		if cleanWord != "" {
			cleanWords = append(cleanWords, cleanWord)
		}
	}

	if len(cleanWords) == 0 {
		return nil, errors.New("нет валидных слов в тексте")
	}

	// Placeholder: леммы = чистые слова, POS tags = "NOUN" для каждого.
	lemmas := cleanWords
	posTags := make(map[string]string)
	for _, word := range cleanWords {
		posTags[word] = "NOUN" // Placeholder для всех слов.
	}

	return &morphological.AnalysisResult{
		Words:   cleanWords,
		Lemmas:  lemmas,
		PosTags: posTags,
	}, nil
}