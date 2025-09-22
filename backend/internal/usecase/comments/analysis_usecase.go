package comments

import (
	"context"
	"strings"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"

	"backend/internal/repository/postgres"
)

// AnalysisUseCase - интерфейс для use cases анализа и статистики комментариев.
type AnalysisUseCase interface {
	AnalyzeKeywords(ctx context.Context, commentID uuid.UUID) (map[string]int, float64, error)
	GetStats(ctx context.Context) (map[string]int64, error)
}

// analysisUseCase - реализация use cases для анализа.
type analysisUseCase struct {
	repo   postgres.CommentRepository
	logger *logrus.Logger
}

// NewAnalysisUseCase создает новый экземпляр use cases для анализа.
func NewAnalysisUseCase(repo postgres.CommentRepository, logger *logrus.Logger) AnalysisUseCase {
	return &analysisUseCase{
		repo:   repo,
		logger: logger,
	}
}

// AnalyzeKeywords проводит простой анализ ключевых слов в комментарии.
// Placeholder для интеграции с keywords module. Использует string matching.
func (uc *analysisUseCase) AnalyzeKeywords(ctx context.Context, commentID uuid.UUID) (map[string]int, float64, error) {
	comment, err := uc.repo.GetByID(ctx, commentID)
	if err != nil {
		return nil, 0, err
	}

	// Простой placeholder: поиск ключевых слов (e.g. "политика", "экономика")
	keywords := []string{"политика", "экономика", "спорт", "технологии"}
	keywordCounts := make(map[string]int)
	textLower := strings.ToLower(comment.Text)

	for _, kw := range keywords {
		count := strings.Count(textLower, kw)
		if count > 0 {
			keywordCounts[kw] = count
		}
	}

	// Простой score: количество найденных ключевых слов
	score := float64(len(keywordCounts))

	// Обновляем флаг analyzed
	comment.Analyzed = true
	err = uc.repo.Update(ctx, comment)
	if err != nil {
		uc.logger.WithError(err).WithField("id", commentID).Error("ошибка обновления флага анализа")
	}

	uc.logger.WithFields(logrus.Fields{
		"comment_id": commentID,
		"keywords":   keywordCounts,
		"score":      score,
	}).Info("анализ ключевых слов завершен")

	return keywordCounts, score, nil
}

// GetStats возвращает статистику комментариев.
// Total, analyzed count, per post (placeholder).
func (uc *analysisUseCase) GetStats(ctx context.Context) (map[string]int64, error) {
	total, err := uc.repo.CountTotal(ctx)
	if err != nil {
		return nil, err
	}

	analyzed, err := uc.repo.CountAnalyzed(ctx)
	if err != nil {
		return nil, err
	}

	stats := map[string]int64{
		"total":      total,
		"analyzed":   analyzed,
		"unanalyzed": total - analyzed,
	}

	uc.logger.Info("статистика комментариев получена")

	return stats, nil
}
