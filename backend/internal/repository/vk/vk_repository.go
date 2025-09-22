package vk

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/go-resty/resty/v2"
	"golang.org/x/time/rate"

	"github.com/example/comment-analysis-backend/internal/config"
	"github.com/example/comment-analysis-backend/internal/domain/vk"
)

type VKRepository interface {
	GetComments(ctx context.Context, ownerID, postID string) ([]*vk.VKComment, error)
	GetPosts(ctx context.Context, ownerID string, count int) ([]*vk.VKPost, error)
	GetLikes(ctx context.Context, type_, ownerID, itemID string) ([]int, error)
}

type vkHTTPClient struct {
	client     *resty.Client
	limiter    *rate.Limiter
	apiVersion string
}

func NewVKRepository(cfg *config.Config) *vkHTTPClient {
	client := resty.New()
	client.SetTimeout(10 * time.Second)
	limiter := rate.NewLimiter(rate.Limit(cfg.VK.RateLimit), cfg.VK.RateLimit)
	return &vkHTTPClient{
		client:     client,
		limiter:    limiter,
		apiVersion: cfg.VK.APIVersion,
	}
}

func (v *vkHTTPClient) GetComments(ctx context.Context, ownerID, postID string) ([]*vk.VKComment, error) {
	if err := v.limiter.Wait(ctx); err != nil {
		return nil, err
	}
	token := os.Getenv("VK_ACCESS_TOKEN")
	if token == "" {
		return nil, fmt.Errorf("VK_ACCESS_TOKEN not set")
	}
	url := fmt.Sprintf("https://api.vk.com/method/wall.getComments?owner_id=%s&post_id=%s&access_token=%s&v=%s", ownerID, postID, token, v.apiVersion)
	resp, err := v.client.R().
		SetContext(ctx).
		Get(url)
	if err != nil {
		return nil, err
	}
	if resp.IsError() {
		return nil, fmt.Errorf("VK API error: %s", resp.String())
	}
	var result struct {
		Response struct {
			Items []struct {
				ID         int64  `json:"id"`
				FromID     int64  `json:"from_id"`
				Date       int64  `json:"date"`
				Text       string `json:"text"`
				LikesCount int    `json:"likes_count"`
				ReplyCount int    `json:"reply_count"`
			} `json:"items"`
		} `json:"response"`
		Error struct {
			ErrorCode int    `json:"error_code"`
			ErrorMsg string `json:"error_msg"`
		} `json:"error"`
	}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}
	if result.Error.ErrorCode != 0 {
		return nil, fmt.Errorf("VK API error %d: %s", result.Error.ErrorCode, result.Error.ErrorMsg)
	}
	comments := make([]*vk.VKComment, len(result.Response.Items))
	for i, item := range result.Response.Items {
		comments[i] = &vk.VKComment{
			ID:         fmt.Sprintf("%d", item.ID),
			FromID:     fmt.Sprintf("%d", item.FromID),
			Date:       item.Date,
			Text:       item.Text,
			LikesCount: item.LikesCount,
			ReplyCount: item.ReplyCount,
		}
	}
	return comments, nil
}

func (v *vkHTTPClient) GetPosts(ctx context.Context, ownerID string, count int) ([]*vk.VKPost, error) {
	if err := v.limiter.Wait(ctx); err != nil {
		return nil, err
	}
	token := os.Getenv("VK_ACCESS_TOKEN")
	if token == "" {
		return nil, fmt.Errorf("VK_ACCESS_TOKEN not set")
	}
	url := fmt.Sprintf("https://api.vk.com/method/wall.get?owner_id=%s&count=%d&access_token=%s&v=%s", ownerID, count, token, v.apiVersion)
	resp, err := v.client.R().
		SetContext(ctx).
		Get(url)
	if err != nil {
		return nil, err
	}
	if resp.IsError() {
		return nil, fmt.Errorf("VK API error: %s", resp.String())
	}
	var result struct {
		Response struct {
			Items []struct {
				ID      int64  `json:"id"`
				OwnerID int64  `json:"owner_id"`
				Text    string `json:"text"`
				Date    int64  `json:"date"`
			} `json:"items"`
		} `json:"response"`
		Error struct {
			ErrorCode int    `json:"error_code"`
			ErrorMsg string `json:"error_msg"`
		} `json:"error"`
	}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}
	if result.Error.ErrorCode != 0 {
		return nil, fmt.Errorf("VK API error %d: %s", result.Error.ErrorCode, result.Error.ErrorMsg)
	}
	posts := make([]*vk.VKPost, len(result.Response.Items))
	for i, item := range result.Response.Items {
		posts[i] = &vk.VKPost{
			ID:      fmt.Sprintf("%d", item.ID),
			OwnerID: fmt.Sprintf("%d", item.OwnerID),
			Text:    item.Text,
			Date:    item.Date,
		}
	}
	return posts, nil
}

func (v *vkHTTPClient) GetLikes(ctx context.Context, type_, ownerID, itemID string) ([]int, error) {
	if err := v.limiter.Wait(ctx); err != nil {
		return nil, err
	}
	token := os.Getenv("VK_ACCESS_TOKEN")
	if token == "" {
		return nil, fmt.Errorf("VK_ACCESS_TOKEN not set")
	}
	url := fmt.Sprintf("https://api.vk.com/method/likes.getList?type=%s&owner_id=%s&item_id=%s&access_token=%s&v=%s", type_, ownerID, itemID, token, v.apiVersion)
	resp, err := v.client.R().
		SetContext(ctx).
		Get(url)
	if err != nil {
		return nil, err
	}
	if resp.IsError() {
		return nil, fmt.Errorf("VK API error: %s", resp.String())
	}
	var result struct {
		Response struct {
			Items []int `json:"users"`
		} `json:"response"`
		Error struct {
			ErrorCode int    `json:"error_code"`
			ErrorMsg string `json:"error_msg"`
		} `json:"error"`
	}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return nil, err
	}
	if result.Error.ErrorCode != 0 {
		return nil, fmt.Errorf("VK API error %d: %s", result.Error.ErrorCode, result.Error.ErrorMsg)
	}
	return result.Response.Items, nil
}