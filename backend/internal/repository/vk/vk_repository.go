// Package vk provides repository for VK API integration.
package vk

import (
	"context"
	"fmt"
	"time"

	"github.com/go-resty/resty/v2"
	"golang.org/x/time/rate"

	"vk-analyzer/internal/domain/vk"
)

// VKRepository defines interface for VK API operations.
type VKRepository interface {
	GetComments(ctx context.Context, ownerID int64, postID int64, token string) ([]vk.VKComment, error)
	GetPosts(ctx context.Context, ownerID int64, count int, offset int, token string) ([]vk.VKPost, error)
	GetLikesList(ctx context.Context, typ string, ownerID int64, itemID int64, token string) ([]int64, error)
	RenewToken(ctx context.Context, userID string) (vk.VKToken, error)
}

// vkRepository implements VKRepository with HTTP client and rate limiting.
type vkRepository struct {
	client  *resty.Client
	limiter *rate.Limiter
}

// NewVKRepository creates new VKRepository instance.
func NewVKRepository() VKRepository {
	client := resty.New()
	client.SetBaseURL("https://api.vk.com")
	limiter := rate.NewLimiter(3, 10) // 3 req/s, burst 10
	return &vkRepository{
		client:  client,
		limiter: limiter,
	}
}

// vkResponse is helper struct for VK API response unmarshaling.
type vkResponse struct {
	Response vkItemsResponse `json:"response"`
}

type vkItemsResponse struct {
	Items interface{} `json:"items"` // Flexible for different types
}

// GetComments fetches comments for a post using VK API wall.getComments.
func (r *vkRepository) GetComments(ctx context.Context, ownerID int64, postID int64, token string) ([]vk.VKComment, error) {
	if err := r.limiter.Wait(ctx); err != nil {
		return nil, fmt.Errorf("rate limit wait: %w", err)
	}

	var comments []vk.VKComment
	err := r.executeWithRetry(ctx, func() (*resty.Response, error) {
		resp, err := r.client.R().
			SetQueryParams(map[string]string{
				"owner_id":     fmt.Sprintf("%d", ownerID),
				"post_id":      fmt.Sprintf("%d", postID),
				"access_token": token,
				"v":            "5.131",
			}).
			SetResult(&vkResponse{
				Response: vkItemsResponse{
					Items: &[]vk.VKComment{},
				},
			}).
			Get("method/wall.getComments")
		if err == nil {
			comments = (*resp.Result().(*vkResponse).Response.Items.(*[]vk.VKComment))
		}
		return resp, err
	})

	return comments, err
}

// GetPosts fetches posts using VK API wall.get with pagination.
func (r *vkRepository) GetPosts(ctx context.Context, ownerID int64, count int, offset int, token string) ([]vk.VKPost, error) {
	if err := r.limiter.Wait(ctx); err != nil {
		return nil, fmt.Errorf("rate limit wait: %w", err)
	}

	var posts []vk.VKPost
	err := r.executeWithRetry(ctx, func() (*resty.Response, error) {
		resp, err := r.client.R().
			SetQueryParams(map[string]string{
				"owner_id":     fmt.Sprintf("%d", ownerID),
				"count":        fmt.Sprintf("%d", count),
				"offset":       fmt.Sprintf("%d", offset),
				"access_token": token,
				"v":            "5.131",
			}).
			SetResult(&vkResponse{
				Response: vkItemsResponse{
					Items: &[]vk.VKPost{},
				},
			}).
			Get("method/wall.get")
		if err == nil {
			posts = (*resp.Result().(*vkResponse).Response.Items.(*[]vk.VKPost))
		}
		return resp, err
	})

	return posts, err
}

// GetLikesList fetches list of user IDs who liked an item using VK API likes.getList.
func (r *vkRepository) GetLikesList(ctx context.Context, typ string, ownerID int64, itemID int64, token string) ([]int64, error) {
	if err := r.limiter.Wait(ctx); err != nil {
		return nil, fmt.Errorf("rate limit wait: %w", err)
	}

	var userIDs []int64
	err := r.executeWithRetry(ctx, func() (*resty.Response, error) {
		resp, err := r.client.R().
			SetQueryParams(map[string]string{
				"type":         typ,
				"owner_id":     fmt.Sprintf("%d", ownerID),
				"item_id":      fmt.Sprintf("%d", itemID),
				"access_token": token,
				"v":            "5.131",
			}).
			SetResult(&vkResponse{
				Response: vkItemsResponse{
					Items: &[]int64{},
				},
			}).
			Get("method/likes.getList")
		if err == nil {
			userIDs = (*resp.Result().(*vkResponse).Response.Items.(*[]int64))
		}
		return resp, err
	})

	return userIDs, err
}

// executeWithRetry performs HTTP request with retry logic for rate limit errors (429).
func (r *vkRepository) executeWithRetry(ctx context.Context, fn func() (*resty.Response, error)) error {
	const maxRetries = 5
	var resp *resty.Response
	var err error

	for attempt := 0; attempt < maxRetries; attempt++ {
		resp, err = fn()
		if err != nil {
			return fmt.Errorf("request failed: %w", err)
		}

		if resp.IsSuccess() {
			return nil
		}

		if resp.StatusCode() == 429 {
			backoff := time.Duration(1<<attempt) * time.Second
			select {
			case <-ctx.Done():
				return ctx.Err()
			case <-time.After(backoff):
			}
			continue
		}

		return fmt.Errorf("VK API error: %d - %s", resp.StatusCode(), resp.String())
	}

	return fmt.Errorf("max retries exceeded for rate limit")
}

// RenewToken renews VK access token for a user.
func (r *vkRepository) RenewToken(ctx context.Context, userID string) (vk.VKToken, error) {
	// This is a placeholder implementation
	// In a real implementation, this would call VK API to refresh the token
	return vk.VKToken{}, fmt.Errorf("token renewal not implemented")
}
