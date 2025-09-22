package comments

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/go-playground/validator/v10"

	"backend/internal/domain/comments"
	"backend/internal/usecase/comments"
	"backend/internal/usecase/users"
	"backend/internal/repository"
)

// CommentsHandler - структура для handlers комментариев.
type CommentsHandler struct {
	useCase         comments.CommentsUseCase
	analysisUseCase comments.AnalysisUseCase
	userUseCase     users.UserUseCase
	validate        *validator.Validate
}

// NewCommentsHandler создает новый экземпляр handlers для комментариев.
func NewCommentsHandler(useCase comments.CommentsUseCase, analysisUseCase comments.AnalysisUseCase, userUseCase users.UserUseCase, validate *validator.Validate) *CommentsHandler {
	return &CommentsHandler{
		useCase:         useCase,
		analysisUseCase: analysisUseCase,
		userUseCase:     userUseCase,
		validate:        validate,
	}
}

// GetCommentsList обрабатывает GET /api/v1/comments - список комментариев с фильтрами.
func (h *CommentsHandler) GetCommentsList(c *gin.Context) {
	var filters repository.ListFilters

	if postIDStr := c.Query("post_id"); postIDStr != "" {
		postID, err := strconv.ParseUint(postIDStr, 10, 64)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "invalid post_id format"})
			return
		}
		filters.PostID = &postID
	}

	if authorIDStr := c.Query("author_id"); authorIDStr != "" {
		authorID, err := strconv.ParseUint(authorIDStr, 10, 64)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "invalid author_id format"})
			return
		}
		filters.AuthorID = &authorID
	}

	if search := c.Query("search"); search != "" {
		filters.Search = search
	}

	if limitStr := c.Query("limit"); limitStr != "" {
		limit, err := strconv.Atoi(limitStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "invalid limit format"})
			return
		}
		filters.Limit = limit
	}

	if offsetStr := c.Query("offset"); offsetStr != "" {
		offset, err := strconv.Atoi(offsetStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "invalid offset format"})
			return
		}
		filters.Offset = offset
	}

	commentsList, err := h.useCase.ListComments(c.Request.Context(), filters)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"comments": commentsList})
}

// GetComment обрабатывает GET /api/v1/comments/:id - получение комментария по ID.
func (h *CommentsHandler) GetComment(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id format"})
		return
	}

	comment, err := h.useCase.GetComment(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, comment)
}

// CreateComment обрабатывает POST /api/v1/comments - создание комментария.
type CreateCommentRequest struct {
	Text     string `json:"text" binding:"required,min=1,max=1000"`
	AuthorID uint   `json:"author_id" binding:"required"`
	PostID   *uint  `json:"post_id,omitempty"`
}

func (h *CommentsHandler) CreateComment(c *gin.Context) {
	var req CreateCommentRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	comment, err := h.useCase.CreateComment(c.Request.Context(), req.Text, req.AuthorID, req.PostID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, comment)
}

// UpdateComment обрабатывает PUT /api/v1/comments/:id - обновление комментария.
type UpdateCommentRequest struct {
	Text string `json:"text" binding:"required,min=1,max=1000"`
}

func (h *CommentsHandler) UpdateComment(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id format"})
		return
	}

	var req UpdateCommentRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Получаем currentUserID из JWT middleware
	currentUserID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not authenticated"})
		return
	}
	currentUserIDUint, ok := currentUserID.(uint)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid user id"})
		return
	}

	comment, err := h.useCase.UpdateComment(c.Request.Context(), id, req.Text, currentUserIDUint)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, comment)
}

// DeleteComment обрабатывает DELETE /api/v1/comments/:id - удаление комментария.
func (h *CommentsHandler) DeleteComment(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id format"})
		return
	}

	currentUserID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not authenticated"})
		return
	}
	currentUserIDUint, ok := currentUserID.(uint)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid user id"})
		return
	}

	err = h.useCase.DeleteComment(c.Request.Context(), id, currentUserIDUint)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "comment deleted successfully"})
}

// AnalyzeKeywords обрабатывает POST /api/v1/comments/keyword-analysis/analyze - анализ ключевых слов.
func (h *CommentsHandler) AnalyzeKeywords(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id format"})
		return
	}

	keywords, score, err := h.analysisUseCase.AnalyzeKeywords(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"keywords": keywords,
		"score":    score,
	})
}

// GetStats обрабатывает GET /api/v1/comments/stats/overview - статистика комментариев.
func (h *CommentsHandler) GetStats(c *gin.Context) {
	stats, err := h.analysisUseCase.GetStats(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, stats)
}