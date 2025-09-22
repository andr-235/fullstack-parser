package vk

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
	"github.com/hibiken/asynq"

	"backend/internal/domain/comments"
	"backend/internal/domain/vk"
	"backend/internal/usecase/comments"
	"backend/internal/usecase/vk"
	"backend/internal/repository/tasks" // assuming TaskRepository for status
)

type VKHandler struct {
	vkCommentsUC *usecase.VKCommentsUseCase
	vkAuthUC     *usecase.VKAuthUseCase
	asynqClient  *asynq.Client
	taskRepo     *repository.TaskRepository
	validate     *validator.Validate
}

func NewVKHandler(vkCommentsUC *usecase.VKCommentsUseCase, vkAuthUC *usecase.VKAuthUseCase, asynqClient *asynq.Client, taskRepo *repository.TaskRepository) *VKHandler {
	return &VKHandler{
		vkCommentsUC: vkCommentsUC,
		vkAuthUC:     vkAuthUC,
		asynqClient:  asynqClient,
		taskRepo:     taskRepo,
		validate:     validator.New(),
	}
}

// FetchCommentsHandler godoc
// @Summary Fetch VK comments for a post
// @Description Fetch comments from VK post asynchronously or synchronously
// @Tags vk
// @Accept json
// @Produce json
// @Param body body FetchCommentsRequest true "Request body"
// @Success 200 {object} []comments.Comment
// @Success 202 {object} TaskResponse
// @Failure 400 {object} ErrorResponse
// @Failure 401 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Security ApiKeyAuth
// @Router /vk/fetch-comments [post]
func (h *VKHandler) FetchCommentsHandler(c *gin.Context) {
	var req FetchCommentsRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.validate.Struct(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Check token
	token, err := h.vkAuthUC.GetToken(c.Request.Context())
	if err != nil {
		if err == usecase.ErrNoToken {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "No VK token available"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// For sync mode, fetch directly (assume flag or default async)
	// Task assumes async by default
	payload, _ := json.Marshal(map[string]interface{}{
		"owner_id": req.OwnerID,
		"post_id":  req.PostID,
		"offset":   req.Offset,
		"count":    req.Count,
		"token":    token,
	})

	task, err := h.asynqClient.Enqueue("vk:fetch_comments", payload)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusAccepted, gin.H{"task_id": task.ID()})
}

type FetchCommentsRequest struct {
	OwnerID string `json:"owner_id" validate:"required"`
	PostID  string `json:"post_id" validate:"required"`
	Offset  int    `json:"offset" validate:"min=0"`
	Count   int    `json:"count" validate:"min=1,max=100"`
}

// GetTaskStatusHandler godoc
// @Summary Get task status and results
// @Description Get status of VK fetch task and comments if completed
// @Tags vk
// @Produce json
// @Param task_id path string true "Task ID"
// @Success 200 {object} TaskStatusResponse
// @Failure 404 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Security ApiKeyAuth
// @Router /vk/task/{task_id} [get]
func (h *VKHandler) GetTaskStatusHandler(c *gin.Context) {
	taskID := c.Param("task_id")

	taskInfo, err := h.asynqClient.GetTaskInfo(taskID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Task not found"})
		return
	}

	status := taskInfo.Status.String()

	var commentList []*comments.Comment
	if status == "Completed" {
		// Assume result stored in taskRepo or Redis
		commentList, err = h.taskRepo.GetTaskResults(c.Request.Context(), taskID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"status":    status,
		"comments":  commentList,
		"completed": status == "Completed",
	})
}

type TaskStatusResponse struct {
	Status   string              `json:"status"`
	Comments []*comments.Comment `json:"comments,omitempty"`
}

// AnalyzeCommentHandler godoc
// @Summary Analyze comment morphologically
// @Description Enqueue morphological analysis for comment
// @Tags comments
// @Produce json
// @Param id path uint true "Comment ID"
// @Success 202 {object} TaskResponse
// @Failure 404 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Security ApiKeyAuth
// @Router /comments/{id}/analyze [post]
func (h *VKHandler) AnalyzeCommentHandler(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid comment ID"})
		return
	}

	comment, err := h.commentsUC.GetByID(c.Request.Context(), uint(id)) // assume commentsUC injected or global
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Comment not found"})
		return
	}

	payload, _ := json.Marshal(map[string]interface{}{
		"comment_id": id,
		"text":       comment.Text,
	})

	task, err := h.asynqClient.Enqueue("morphological:analyze", payload)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusAccepted, gin.H{"task_id": task.ID()})
}

type TaskResponse struct {
	TaskID string `json:"task_id"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}