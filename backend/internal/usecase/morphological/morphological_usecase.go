package morphological

import (
	"errors"
	"strings"
	"unicode"

	"backend/internal/domain/morphological"
	"backend/internal/usecase/morphological/morphological_service"
	"github.com/sirupsen/logrus"
)

// Константы для валидации.
const (
	MaxTextLength = 1000
	MinTextLength = 1
)

// MorphologicalRepository определяет интерфейс для хранения результатов анализа (optional).
type MorphologicalRepository interface {
	SaveResult(textHash string, result *morphological.AnalysisResult) error
}

// MorphologicalUsecase определяет интерфейс для бизнес-логики морфологического анализа.
type MorphologicalUsecase interface {
	AnalyzeText(req *morphological.TextRequest) (*morphological.AnalysisResult, error)
}

// morphologicalUsecase - имплементация usecase.
type morphologicalUsecase struct {
	service MorphologyService
	repo    MorphologicalRepository // Optional.
	logger  *logrus.Logger
}

// NewMorphologicalUsecase создаёт новый usecase для морфологического анализа.
func NewMorphologicalUsecase(service morphological_service.MorphologyService, repo MorphologicalRepository, logger *logrus.Logger) MorphologicalUsecase {
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
		uc.logger.WithError(err).Error("ошибка анализа текста")
		return nil, err
	}

	// Optional: сохранение в репозиторий.
	if uc.repo != nil {
		textHash := uc.hashText(req.Text) // Простой хеш для идентификации.
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
	length := len(text)
	if length < MinTextLength || length > MaxTextLength {
		return errors.New("длина текста должна быть от 1 до 1000 символов")
	}

	// Проверка на разрешённые символы: буквы, пробелы, базовая пунктуация, цифры.
	for _, r := range text {
		if !unicode.IsLetter(r) && !unicode.IsSpace(r) && !unicode.IsPunct(r) && !unicode.IsNumber(r) {
			return errors.New("текст содержит недопустимые символы")
		}
	}

	return nil
}

// hashText - простой хеш для текста (placeholder, можно заменить на sha256).
func (uc *morphologicalUsecase) hashText(text string) string {
	return strings.ToLower(text) // Простой placeholder хеш.
}