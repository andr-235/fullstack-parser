package vk

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"time"

	domainvk "vk-analyzer/internal/domain/vk"
	repovk "vk-analyzer/internal/repository/vk"

	"github.com/redis/go-redis/v9"
)

// VKAuthUseCase encapsulates the business logic for VK authentication,
// including token storage, retrieval, and renewal using Redis for caching.
type VKAuthUseCase struct {
	repo        repovk.VKRepository
	redisClient *redis.Client
}

// NewVKAuthUseCase creates a new instance of VKAuthUseCase with dependency injection.
func NewVKAuthUseCase(repo repovk.VKRepository, redisClient *redis.Client) *VKAuthUseCase {
	return &VKAuthUseCase{
		repo:        repo,
		redisClient: redisClient,
	}
}

// StoreToken stores the VK token in Redis with TTL based on the token's expiration time.
// It serializes the token to JSON for storage.
func (uc *VKAuthUseCase) StoreToken(ctx context.Context, token domainvk.VKToken) error {
	key := fmt.Sprintf("vk:token:%d", token.UserID)
	data, err := json.Marshal(token)
	if err != nil {
		return fmt.Errorf("failed to marshal token: %w", err)
	}
	ttl := time.Until(token.ExpiresAt)
	if ttl <= 0 {
		ttl = 24 * time.Hour // Default TTL if already expired
	}
	return uc.redisClient.Set(ctx, key, data, ttl).Err()
}

// GetToken retrieves the VK token from Redis by user ID.
// If not found, attempts to use VK_ACCESS_TOKEN from env as fallback.
// It deserializes the JSON data back to VKToken struct.
func (uc *VKAuthUseCase) GetToken(ctx context.Context, userID string) (domainvk.VKToken, error) {
	key := fmt.Sprintf("vk:token:%s", userID)
	data, err := uc.redisClient.Get(ctx, key).Result()
	if err != nil {
		// Fallback to env token if not in Redis
		accessToken := os.Getenv("VK_ACCESS_TOKEN")
		if accessToken == "" {
			return domainvk.VKToken{}, fmt.Errorf("no token found for user %s and no VK_ACCESS_TOKEN in env: %w", userID, err)
		}
		// Create a default token from env (assuming no expires for simplicity)
		userIDInt, _ := strconv.ParseInt(userID, 10, 64)
		return domainvk.VKToken{
			AccessToken: accessToken,
			UserID:      userIDInt,
			ExpiresAt:   time.Now().Add(24 * time.Hour),
		}, nil
	}
	var token domainvk.VKToken
	if err := json.Unmarshal([]byte(data), &token); err != nil {
		return domainvk.VKToken{}, fmt.Errorf("failed to unmarshal token: %w", err)
	}
	return token, nil
}

// RenewToken renews the VK token if it is expired by calling the repository to update via VK API,
// then stores the new token in Redis.
func (uc *VKAuthUseCase) RenewToken(ctx context.Context, token domainvk.VKToken) error {
	if time.Now().After(token.ExpiresAt) {
		userID := fmt.Sprintf("%d", token.UserID)
		newToken, err := uc.repo.RenewToken(ctx, userID)
		if err != nil {
			return fmt.Errorf("failed to renew token via VK API: %w", err)
		}
		return uc.StoreToken(ctx, newToken)
	}
	// Token is still valid, no action needed.
	return nil
}
