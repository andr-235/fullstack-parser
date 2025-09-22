package vk

import (
	"context"

	"backend/internal/domain/vk"
	"backend/internal/logger"
	"backend/internal/repository"
)

type VKPostsUseCase struct {
	vkRepo repository.VKRepository
	log    logger.Logger
}

func NewVKPostsUseCase(vkRepo repository.VKRepository, log logger.Logger) *VKPostsUseCase {
	return &VKPostsUseCase{
		vkRepo: vkRepo,
		log:    log,
	}
}

func (uc *VKPostsUseCase) FetchPosts(ctx context.Context, ownerID string, count int) ([]*vk.VKPost, error) {
	uc.log.Info(ctx, "Fetching VK posts", logger.Fields{
		"owner_id": ownerID,
		"count":    count,
	})

	// Call repository to get posts
	posts, err := uc.vkRepo.GetPosts(ctx, ownerID, count)
	if err != nil {
		uc.log.Error(ctx, "Failed to fetch posts from VK", logger.Fields{"error": err, "owner_id": ownerID})
		return nil, err
	}

	// Filter by owner_id if needed (assume repo already filters)
	// For now, assume all returned are for owner_id

	uc.log.Info(ctx, "Successfully fetched posts", logger.Fields{"count": len(posts), "owner_id": ownerID})
	return posts, nil
}