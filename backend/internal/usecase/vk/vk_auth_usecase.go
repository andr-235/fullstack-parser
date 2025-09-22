package vk

import (
	"context"
	"time"

	"backend/internal/domain/vk"
	"backend/internal/repository"
	"backend/internal/logger"
	"github.com/google/uuid"
)

type VKAuthUseCase struct {
	vkRepo      repository.VKRepository
	redisRepo   repository.RedisRepository
	log         logger.Logger
	tokenTTL    time.Duration
}

func NewVKAuthUseCase(vkRepo repository.VKRepository, redisRepo repository.RedisRepository, log logger.Logger) *VKAuthUseCase {
	return &VKAuthUseCase{
		vkRepo:    vkRepo,
		redisRepo: redisRepo,
		log:       log,
		tokenTTL:  24 * time.Hour, // 86400s
	}
}

// Authenticate handles VK Implicit Flow authentication (stub for now).
// In real implementation, exchange code for token via VK API.
func (uc *VKAuthUseCase) Authenticate(ctx context.Context, code string) (*vk.VKToken, error) {
	uc.log.Info(ctx, "Starting VK authentication with code", logger.Fields{"code": code[:10]+"..."})

	// Stub: In real, call VK API to get token from code
	// For demo, create mock token
	token := &vk.VKToken{
		ID:        uuid.New(),
		AccessToken: "mock_vk_access_token_" + code,
		ExpiresAt:  time.Now().Add(24 * time.Hour),
		UserID:     12345, // Mock user ID
	}

	if err := token.Validate(); err != nil {
		uc.log.Error(ctx, "Invalid token after authentication", logger.Fields{"error": err})
		return nil, err
	}

	uc.log.Info(ctx, "VK authentication successful")
	return token, nil
}

// StoreToken stores VK token in Redis with TTL.
func (uc *VKAuthUseCase) StoreToken(ctx context.Context, token *vk.VKToken) error {
	uc.log.Info(ctx, "Storing VK token in Redis", logger.Fields{"token_id": token.ID})

	key := "vk:token:" + token.ID.String()
	data, err := token.MarshalJSON() // Assume VKToken has MarshalJSON
	if err != nil {
		uc.log.Error(ctx, "Failed to marshal token", logger.Fields{"error": err})
		return err
	}

	if err := uc.redisRepo.Set(ctx, key, data, uc.tokenTTL); err != nil {
		uc.log.Error(ctx, "Failed to store token in Redis", logger.Fields{"error": err})
		return err
	}

	uc.log.Info(ctx, "VK token stored successfully")
	return nil
}

// GetToken retrieves VK token from Redis.
func (uc *VKAuthUseCase) GetToken(ctx context.Context, tokenID uuid.UUID) (*vk.VKToken, error) {
	uc.log.Info(ctx, "Retrieving VK token from Redis", logger.Fields{"token_id": tokenID})

	key := "vk:token:" + tokenID.String()
	data, err := uc.redisRepo.Get(ctx, key)
	if err != nil {
		uc.log.Error(ctx, "Failed to get token from Redis", logger.Fields{"error": err, "token_id": tokenID})
		return nil, err
	}

	token := &vk.VKToken{}
	if err := token.UnmarshalJSON(data); err != nil { // Assume UnmarshalJSON
		uc.log.Error(ctx, "Failed to unmarshal token", logger.Fields{"error": err})
		return nil, err
	}

	if token.IsExpired() {
		uc.log.Warn(ctx, "VK token expired", logger.Fields{"token_id": tokenID})
		return nil, repository.ErrTokenExpired
	}

	uc.log.Info(ctx, "VK token retrieved successfully")
	return token, nil
}

// RefreshToken refreshes expired token (stub).
func (uc *VKAuthUseCase) RefreshToken(ctx context.Context, token *vk.VKToken) error {
	if !token.IsExpired() {
		return nil
	}

	uc.log.Info(ctx, "Refreshing VK token", logger.Fields{"token_id": token.ID})

	// Stub: In real, call VK API to refresh
	token.ExpiresAt = time.Now().Add(24 * time.Hour)

	if err := uc.StoreToken(ctx, token); err != nil {
		return err
	}

	uc.log.Info(ctx, "VK token refreshed successfully")
	return nil
}