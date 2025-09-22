package postgres

import (
	"context"

	"gorm.io/gorm"

	"backend/internal/domain"
	"backend/internal/logger"
)

// MorphologicalRepository defines the interface for morphological analysis storage.
type MorphologicalRepository interface {
	SaveAnalysis(ctx context.Context, commentID uint, analysis *domain.TextAnalysis) error
	GetAnalysis(ctx context.Context, commentID uint) (*domain.TextAnalysis, error)
}

// morphologicalRepository is the PostgreSQL implementation of MorphologicalRepository.
type morphologicalRepository struct {
	db     *gorm.DB
	logger logger.Logger
}

// NewMorphologicalRepository creates a new MorphologicalRepository.
func NewMorphologicalRepository(db *gorm.DB, lg logger.Logger) MorphologicalRepository {
	return &morphologicalRepository{
		db:     db,
		logger: lg,
	}
}

// SaveAnalysis saves the analysis result to the Comment's Analysis field as JSON.
func (r *morphologicalRepository) SaveAnalysis(ctx context.Context, commentID uint, analysis *domain.TextAnalysis) error {
	var comment domain.Comment
	if err := r.db.WithContext(ctx).First(&comment, commentID).Error; err != nil {
		r.logger.Error(ctx, "Failed to find comment for analysis save", logger.Fields{"comment_id": commentID, "error": err})
		return err
	}

	// Update analysis fields
	comment.Analysis = analysis
	comment.Keywords = analysis.Keywords
	comment.Tone = analysis.Tone

	if err := r.db.WithContext(ctx).Save(&comment).Error; err != nil {
		r.logger.Error(ctx, "Failed to save analysis", logger.Fields{"comment_id": commentID, "error": err})
		return err
	}

	r.logger.Info(ctx, "Analysis saved successfully", logger.Fields{"comment_id": commentID})
	return nil
}

// GetAnalysis retrieves the analysis for a comment.
func (r *morphologicalRepository) GetAnalysis(ctx context.Context, commentID uint) (*domain.TextAnalysis, error) {
	var comment domain.Comment
	if err := r.db.WithContext(ctx).First(&comment, commentID).Error; err != nil {
		r.logger.Error(ctx, "Failed to find comment for analysis get", logger.Fields{"comment_id": commentID, "error": err})
		return nil, err
	}

	if comment.Analysis == nil {
		return nil, nil // No analysis yet
	}

	r.logger.Info(ctx, "Analysis retrieved successfully", logger.Fields{"comment_id": commentID})
	return comment.Analysis, nil
}