package vk

import (
	"time"
)

type VKToken struct {
	AccessToken string    `json:"access_token"`
	Expiry      time.Time `json:"expiry"`
}

func (t *VKToken) IsExpired() bool {
	return time.Now().After(t.Expiry)
}

func (t *VKToken) Refresh() error {
	// Заглушка для обновления токена
	return nil
}