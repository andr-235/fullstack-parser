package morphological

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"strings"

	"github.com/go-resty/resty/v2"
	"github.com/prometheus/client_golang/prometheus"

	"backend/internal/domain"
	"backend/internal/logger"
	"backend/internal/repository"
)

type MorphologicalUseCase struct {
	commentRepo  repository.CommentRepository
	morphRepo    repository.MorphologicalRepository
	logger       logger.Logger
	metrics      *prometheus.CounterVec
}

func NewMorphologicalUseCase(commentRepo repository.CommentRepository, morphRepo repository.MorphologicalRepository, lg logger.Logger) *MorphologicalUseCase {
	return &MorphologicalUseCase{
		commentRepo: commentRepo,
		morphRepo:   morphRepo,
		logger:      lg,
		metrics: prometheus.NewCounterVec(prometheus.CounterOpts{
			Name: "morphological_analysis_calls_total",
			Help: "Total number of morphological analysis calls",
		}),
	}
}

func (uc *MorphologicalUseCase) Analyze(ctx context.Context, text string) (*domain.TextAnalysis, error) {
	uc.logger.Info(ctx, "Starting morphological analysis", logger.Fields{"text_length": len(text)})

	uc.metrics.WithLabelValues("analyze").Inc()

	// Mock external API call using resty
	client := resty.New()
	resp, err := client.R().
		SetHeader("Content-Type", "application/json").
		SetBody(map[string]string{"text": text}).
		Post("https://api.ya.ru/analyze") // Stub URL, in real use actual Yandex API endpoint

	if err != nil || resp.StatusCode() != http.StatusOK {
		uc.logger.Warn(ctx, "External API failed, using fallback stub", logger.Fields{"error": err})
		// Fallback to simple stub
		return uc.simpleAnalyze(ctx, text)
	}

	var apiResp struct {
		Keywords []string `json:"keywords"`
		Tone     string   `json:"tone"`
		Entities map[string][]string `json:"entities"`
		Score    float64  `json:"score"`
	}
	if err := json.Unmarshal(resp.Body(), &apiResp); err != nil {
		uc.logger.Warn(ctx, "Failed to parse API response, using fallback", logger.Fields{"error": err})
		return uc.simpleAnalyze(ctx, text)
	}

	uc.logger.Info(ctx, "External API analysis successful")
	return &domain.TextAnalysis{
		Keywords: apiResp.Keywords,
		Tone:     apiResp.Tone,
		Entities: apiResp.Entities,
		Score:    apiResp.Score,
	}, nil
}

// simpleAnalyze is a fallback stub for morphological analysis.
func (uc *MorphologicalUseCase) simpleAnalyze(text string) (*domain.TextAnalysis, error) {
	uc.logger.Info(ctx, "Using simple fallback analysis")
	// Simple keyword extraction: split by space, take first 5 words as keywords
	words := strings.Split(text, " ")
	if len(words) > 5 {
		words = words[:5]
	}
	return &domain.TextAnalysis{
		Keywords: words,
		Tone:     "neutral",
		Entities: map[string][]string{},
		Score:    0.5,
	}, nil
}

// AnalyzeCommentsBatch performs batch analysis for multiple comments.
// For now, stub; in production, batch process and update comments.
func (uc *MorphologicalUseCase) AnalyzeCommentsBatch(ctx context.Context, commentIDs []uint) error {
	// Stub: no-op, actual implementation would fetch, analyze, update via repo
	return nil
}