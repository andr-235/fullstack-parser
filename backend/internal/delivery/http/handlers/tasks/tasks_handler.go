package tasks

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"backend/internal/domain/tasks" as domain_tasks
	"backend/internal/usecase/tasks" as usecase
)

// TasksHandler - обработчики HTTP для задач.
type TasksHandler struct {
	usecase *usecase.TasksUsecase
}

// NewTasksHandler создает новый handler для задач.
func NewTasksHandler(usecase *usecase.TasksUsecase) *TasksHandler {
	return &TasksHandler{usecase: usecase}
}

// EnqueueTask handler для постановки задачи.
func (h *TasksHandler) EnqueueTask(c *gin.Context) {
	var req domain_tasks.EnqueueRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		logrus.WithError(err).Error("Неверный формат запроса на постановку задачи")
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	id, err := h.usecase.EnqueueTask(c.Request.Context(), &req)
	if err != nil {
		logrus.WithError(err).Error("Ошибка постановки задачи")
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"task_id": id})
}

// GetTaskStatus handler для получения статуса задачи.
func (h *TasksHandler) GetTaskStatus(c *gin.Context) {
	id := c.Param("id")
	resp, err := h.usecase.GetTaskStatus(c.Request.Context(), id)
	if err != nil {
		logrus.WithError(err).WithField("task_id", id).Error("Ошибка получения статуса задачи")
		if strings.Contains(err.Error(), "не найдена") {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	c.JSON(http.StatusOK, resp)
}

// CancelTask handler для отмены задачи.
func (h *TasksHandler) CancelTask(c *gin.Context) {
	id := c.Param("id")
	err := h.usecase.CancelTask(c.Request.Context(), id)
	if err != nil {
		logrus.WithError(err).WithField("task_id", id).Error("Ошибка отмены задачи")
		if strings.Contains(err.Error(), "не найдена") {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Задача отменена"})
}

// ListTasks handler для списка задач.
func (h *TasksHandler) ListTasks(c *gin.Context) {
	var req domain_tasks.ListRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		logrus.WithError(err).Error("Неверный формат запроса на список задач")
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := h.usecase.ListTasks(c.Request.Context(), &req)
	if err != nil {
		logrus.WithError(err).Error("Ошибка получения списка задач")
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, resp)
}

// GetStats handler для статистики очередей.
func (h *TasksHandler) GetStats(c *gin.Context) {
	stats, err := h.usecase.GetStats(c.Request.Context())
	if err != nil {
		logrus.WithError(err).Error("Ошибка получения статистики")
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, stats)
}