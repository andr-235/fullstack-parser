package comments

// Donut represents VK Donut information
type Donut struct {
	IsDon       bool   `json:"is_don"`
	Placeholder string `json:"placeholder"`
}

// Likes represents information about comment likes
type Likes struct {
	Count     int `json:"count"`
	UserLikes int `json:"user_likes"`
	CanLike   int `json:"can_like"`
}

// Thread represents information about nested comment thread
type Thread struct {
	Count           int       `json:"count"`
	Items           []Comment `json:"items,omitempty"`
	CanPost         bool      `json:"can_post"`
	ShowReplyButton bool      `json:"show_reply_button"`
	GroupsCanPost   bool      `json:"groups_can_post"`
}

// Comment represents a wall comment entity according to VK API.
type Comment struct {
	ID             int64         `json:"id"`
	FromID         int64         `json:"from_id"`
	Date           int64         `json:"date"` // Unix timestamp
	Text           string        `json:"text"`
	Donut          *Donut        `json:"donut,omitempty"`
	ReplyToUser    *int64        `json:"reply_to_user,omitempty"`
	ReplyToComment *int64        `json:"reply_to_comment,omitempty"`
	Attachments    []interface{} `json:"attachments,omitempty"` // Will be properly typed based on VK API
	ParentsStack   []int64       `json:"parents_stack,omitempty"`
	Thread         *Thread       `json:"thread,omitempty"`
	Likes          *Likes        `json:"likes,omitempty"` // VK API likes information

	// Additional processed fields for our domain
	Keywords  []string `json:"keywords,omitempty"`
	Sentiment string   `json:"sentiment,omitempty"`
	TaskID    string   `json:"task_id,omitempty"`
}
