// Package morphological содержит use cases для морфологического анализа текста.
// Предоставляет бизнес-логику для анализа текста, валидации и сохранения результатов.
package morphological

import (
	"errors"
	"strings"
	"unicode"

	"backend/internal/domain/morphological"

	"github.com/sirupsen/logrus"
)

// Константы для валидации текста.
const (
	MaxTextLength = 1000 // Максимальная длина текста для анализа
	MinTextLength = 1    // Минимальная длина текста для анализа
)

// MorphologicalRepository определяет интерфейс для хранения результатов анализа (optional).
type MorphologicalRepository interface {
	SaveResult(textHash string, result *morphological.AnalysisResult) error
}

// MorphologicalUsecase определяет интерфейс для бизнес-логики морфологического анализа.
type MorphologicalUsecase interface {
	AnalyzeText(req *morphological.TextRequest) (*morphological.AnalysisResult, error)
	ValidateText(text string) error
	GetTextHash(text string) string
}

// morphologicalUsecase - имплементация usecase.
type morphologicalUsecase struct {
	service MorphologyService
	repo    MorphologicalRepository // Optional.
	logger  *logrus.Logger
}

// NewMorphologicalUsecase создаёт новый usecase для морфологического анализа.
func NewMorphologicalUsecase(service MorphologyService, repo MorphologicalRepository, logger *logrus.Logger) MorphologicalUsecase {
	return &morphologicalUsecase{
		service: service,
		repo:    repo,
		logger:  logger,
	}
}

// AnalyzeText выполняет анализ текста: валидация, вызов сервиса, optional сохранение, логирование.
func (uc *morphologicalUsecase) AnalyzeText(req *morphological.TextRequest) (*morphological.AnalysisResult, error) {
	// Валидация входного текста.
	if err := uc.validateText(req.Text); err != nil {
		uc.logger.WithError(err).WithField("text_length", len(req.Text)).Error("ошибка валидации текста")
		return nil, err
	}

	// Вызов сервиса анализа.
	result, err := uc.service.AnalyzeText(req.Text)
	if err != nil {
		uc.logger.WithError(err).WithField("text_length", len(req.Text)).Error("ошибка анализа текста")
		return nil, err
	}

	// Валидация результата анализа.
	if result == nil {
		uc.logger.Error("сервис анализа вернул nil результат")
		return nil, errors.New("ошибка анализа: получен пустой результат")
	}

	// Optional: сохранение в репозиторий.
	if uc.repo != nil {
		textHash := uc.hashText(req.Text)
		if saveErr := uc.repo.SaveResult(textHash, result); saveErr != nil {
			uc.logger.WithError(saveErr).WithField("text_hash", textHash).Warn("не удалось сохранить результат анализа")
			// Не фатально, продолжаем.
		} else {
			uc.logger.WithField("text_hash", textHash).WithField("word_count", len(result.Words)).Info("результат анализа сохранён")
		}
	}

	uc.logger.WithField("word_count", len(result.Words)).Info("анализ текста завершён успешно")
	return result, nil
}

// validateText проверяет длину и символы текста (алфавит + пробелы, русский/английский).
func (uc *morphologicalUsecase) validateText(text string) error {
	// Проверка на пустую строку
	if text == "" {
		return errors.New("текст не может быть пустым")
	}

	// Проверка длины
	length := len(text)
	if length < MinTextLength || length > MaxTextLength {
		return errors.New("длина текста должна быть от 1 до 1000 символов")
	}

	// Проверка на разрешённые символы: буквы, пробелы, базовая пунктуация, цифры.
	invalidChars := make([]rune, 0)
	for _, r := range text {
		if !unicode.IsLetter(r) && !unicode.IsSpace(r) && !unicode.IsPunct(r) && !unicode.IsNumber(r) {
			invalidChars = append(invalidChars, r)
		}
	}

	if len(invalidChars) > 0 {
		uc.logger.WithField("invalid_chars", string(invalidChars)).Warn("найдены недопустимые символы")
		return errors.New("текст содержит недопустимые символы")
	}

	return nil
}

// hashText создает простой хеш для текста (placeholder, можно заменить на sha256).
func (uc *morphologicalUsecase) hashText(text string) string {
	// Нормализация текста: приведение к нижнему регистру и удаление лишних пробелов
	normalized := strings.ToLower(strings.TrimSpace(text))
	// Простой хеш на основе длины и первых/последних символов
	if len(normalized) == 0 {
		return "empty"
	}
	return normalized[:min(10, len(normalized))]
}

// ValidateText проверяет валидность текста для анализа.
func (uc *morphologicalUsecase) ValidateText(text string) error {
	return uc.validateText(text)
}

// GetTextHash возвращает хеш текста для идентификации.
func (uc *morphologicalUsecase) GetTextHash(text string) string {
	return uc.hashText(text)
}

// min возвращает минимальное из двух чисел.
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
