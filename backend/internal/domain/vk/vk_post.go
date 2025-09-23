package vk

import "time"

// VKPost представляет пост из VK API.
type VKPost struct {
	ID      int64     `json:"id"`
	OwnerID int64     `json:"owner_id"`
	Text    string    `json:"text"`
	Date    time.Time `json:"date"`
	// Другие базовые поля можно добавить по необходимости.
}