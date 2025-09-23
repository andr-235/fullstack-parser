package vk

import (
	"net/http"
	"strconv"

	"vk-analyzer/internal/usecase/vk"

	"github.com/gin-gonic/gin"
)

// VKHandler обрабатывает HTTP-запросы для VK API endpoints.
type VKHandler struct {
	commentsUC *vk.VKCommentsUseCase
}

// NewVKHandler создает новый экземпляр VKHandler с зависимостью от use case.
func NewVKHandler(uc *vk.VKCommentsUseCase) *VKHandler {
	return &VKHandler{
		commentsUC: uc,
	}
}

// FetchComments обрабатывает POST /api/vk/fetch-comments.
// Принимает JSON {owner_id: int, post_id: int}, вызывает use case для запуска задачи,
// возвращает {task_id: string}.
func (h *VKHandler) FetchComments(c *gin.Context) {
	type requestBody struct {
		OwnerID int `json:"owner_id" binding:"required"`
		PostID  int `json:"post_id" binding:"required"`
	}

	var req requestBody
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body: " + err.Error()})
		return
	}

	taskID, err := h.commentsUC.FetchComments(c.Request.Context(), req.OwnerID, req.PostID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch comments: " + err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"task_id": taskID})
}

// TaskStatus обрабатывает GET /api/vk/task/{task_id}.
// Извлекает task_id из params, вызывает use case для получения статуса и комментариев,
// возвращает {status: string, comments: []Comment}.
func (h *VKHandler) TaskStatus(c *gin.Context) {
	taskID := c.Param("task_id")
	if taskID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Task ID is required"})
		return
	}

	status, commentList, err := h.commentsUC.GetCommentsByTaskID(c.Request.Context(), taskID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get task status: " + err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":   status,
		"comments": commentList,
	})
}

// ListComments обрабатывает GET /api/comments.
// Принимает query params для фильтрации (например, ?task_id=string&limit=int), возвращает список domain.Comment.
func (h *VKHandler) ListComments(c *gin.Context) {
	taskID := c.Query("task_id")
	limitStr := c.Query("limit")
	limit := 10 // default
	if limitStr != "" {
		l, err := strconv.Atoi(limitStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid limit: " + err.Error()})
			return
		}
		limit = l
	}

	commentList, err := h.commentsUC.ListComments(c.Request.Context(), taskID, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list comments: " + err.Error()})
		return
	}

	c.JSON(http.StatusOK, commentList)
}
