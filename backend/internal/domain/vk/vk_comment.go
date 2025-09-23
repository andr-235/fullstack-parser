package vk

import "time"

// VKComment представляет комментарий из VK API.
type VKComment struct {
	ID       int64     `json:"id"`
	FromID   int64     `json:"from_id"`
	Date     time.Time `json:"date"`
	Text     string    `json:"text"`
	Likes    int       `json:"likes_count"`
	// Другие поля можно добавить по необходимости, e.g. attachments.
}