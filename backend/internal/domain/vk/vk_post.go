package vk

type VKPost struct {
	ID      string `json:"id"`
	OwnerID string `json:"owner_id"`
	Text    string `json:"text"`
	Date    int64  `json:"date"`
}