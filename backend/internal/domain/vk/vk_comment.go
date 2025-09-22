package vk

import (
	"errors"
)

type VKComment struct {
	ID         string `json:"id"`
	FromID     string `json:"from_id"`
	Date       int64  `json:"date"`
	Text       string `json:"text"`
	LikesCount int    `json:"likes_count"`
	ReplyCount int    `json:"reply_count"`
}

func (c *VKComment) Validate() error {
	if c.ID == "" {
		return errors.New("id is required")
	}
	if c.Text == "" {
		return errors.New("text is required")
	}
	return nil
}