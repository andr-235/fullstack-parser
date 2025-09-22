package vk

import (
	"context"
	"errors"
	"math"
	"strconv"
	"strings"

	"backend/internal/domain"
	"backend/internal/domain/vk"
	"backend/internal/logger"
	"backend/internal/repository"
)

var (
	ErrInvalidOwnerID = errors.New("invalid owner ID: must be numeric")
	ErrInvalidCount   = errors.New("invalid count: must be positive and <= 100")
)

type FetchCommentsRequest struct {
	OwnerID string `json:"owner_id" validate:"required"`
	PostID  string `json:"post_id" validate:"required"`
	Offset  int    `json:"offset" validate:"min=0"`
	Count   int    `json:"count" validate:"min=1,max=100"`
}

type FetchCommentsResponse struct {
	Comments []*domain.Comment `json:"comments"`
	Total    int               `json:"total"`
}

type VKCommentsUseCase struct {
	vkRepo       repository.VKRepository
	commentRepo  repository.CommentRepository
	log          logger.Logger
}

func NewVKCommentsUseCase(vkRepo repository.VKRepository, commentRepo repository.CommentRepository, log logger.Logger) *VKCommentsUseCase {
	return &VKCommentsUseCase{
		vkRepo:      vkRepo,
		commentRepo: commentRepo,
		log:         log,
	}
}

func (uc *VKCommentsUseCase) FetchComments(ctx context.Context, req FetchCommentsRequest) (*FetchCommentsResponse, error) {
	uc.log.Info(ctx, "Fetching VK comments", logger.Fields{
		"owner_id": req.OwnerID,
		"post_id":  req.PostID,
		"offset":   req.Offset,
		"count":    req.Count,
	})

	// Validation
	if _, err := strconv.ParseInt(req.OwnerID, 10, 64); err != nil || strings.HasPrefix(req.OwnerID, "-") && len(req.OwnerID) == 1 {
		uc.log.Warn(ctx, "Invalid owner ID", logger.Fields{"owner_id": req.OwnerID, "error": ErrInvalidOwnerID})
		return nil, ErrInvalidOwnerID
	}
	req.Count = int(math.Min(float64(req.Count), 100))

	// Call repository
	vkComments, total, err := uc.vkRepo.GetComments(ctx, req.OwnerID, req.PostID, map[string]interface{}{
		"offset": req.Offset,
		"count":  req.Count,
	})
	if err != nil {
		uc.log.Error(ctx, "Failed to get comments from VK", logger.Fields{"error": err})
		return nil, err
	}

	// Mapping VKComment to domain.Comment
	comments := make([]*domain.Comment, 0, len(vkComments))
	for _, vc := range vkComments {
		comment := &domain.Comment{
			ID:      0, // Will be set by DB
			Text:    vc.Text,
			Date:    vc.Date,
			UserID:  vc.FromID, // Map from_id to user_id
			PostID:  req.PostID, // Assume post_id as external ref
			Source:  "vk", // Mark source
			// Other fields as per domain.Comment
		}
		if err := comment.Validate(); err != nil {
			uc.log.Warn(ctx, "Invalid comment after mapping", logger.Fields{"error": err, "vk_comment_id": vc.ID})
			continue
		}
		comments = append(comments, comment)
	}

	// Save to PostgreSQL
	for _, comment := range comments {
		if err := uc.commentRepo.Create(ctx, comment); err != nil {
			uc.log.Error(ctx, "Failed to save comment", logger.Fields{"error": err, "comment_id": comment.ID})
			// Continue or return? For now continue
		}
	}

	resp := &FetchCommentsResponse{
		Comments: comments,
		Total:    total,
	}

	uc.log.Info(ctx, "Successfully fetched and saved comments", logger.Fields{"count": len(comments), "total": total})
	return resp, nil
}