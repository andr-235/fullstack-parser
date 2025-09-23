package vk

import "time"

// VKToken представляет токен доступа VK.
type VKToken struct {
	AccessToken string    `json:"access_token"`
	ExpiresIn   int       `json:"expires_in"`
	UserID      int64     `json:"user_id"`
	ExpiresAt   time.Time `json:"expires_at,omitempty"`
}
