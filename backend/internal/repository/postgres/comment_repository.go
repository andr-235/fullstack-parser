package postgres

import (
	"vk-analyzer/internal/domain/comments"

	"gorm.io/gorm"
)

type CommentRepository interface {
	CreateMany([]comments.Comment) error
	GetByID(int64) (*comments.Comment, error)
	Update(*comments.Comment) error
}

type commentRepository struct {
	db *gorm.DB
}

func NewCommentRepository(db *gorm.DB) CommentRepository {
	return &commentRepository{db: db}
}

func (r *commentRepository) CreateMany(comments []comments.Comment) error {
	return r.db.Create(&comments).Error
}

func (r *commentRepository) GetByID(id int64) (*comments.Comment, error) {
	var c comments.Comment
	err := r.db.First(&c, id).Error
	if err != nil {
		return nil, err
	}
	return &c, nil
}

func (r *commentRepository) Update(c *comments.Comment) error {
	return r.db.Save(c).Error
}