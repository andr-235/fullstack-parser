package main

import (
	"log"

	vkhandlers "vk-analyzer/internal/delivery/http/handlers/vk"
	vkuc "vk-analyzer/internal/usecase/vk"

	"github.com/gin-gonic/gin"
)

// main инициализирует и запускает API сервер.
func main() {
	// Dependency Injection: инициализация use case (placeholder, wired с repositories позже).
	commentsUC := vkuc.NewVKCommentsUseCase(nil) // Заменить на реальные зависимости (VKRepository, AsynqClient и т.д.)

	// Инициализация handler.
	vkHandler := vkhandlers.NewVKHandler(commentsUC)

	// Инициализация Gin роутера.
	r := gin.Default()

	// Группа для VK API endpoints.
	vkGroup := r.Group("/api/vk")
	{
		vkGroup.POST("/fetch-comments", vkHandler.FetchComments)
		vkGroup.GET("/task/:task_id", vkHandler.TaskStatus)
	}

	// Endpoint для списка комментариев (по ТЗ).
	r.GET("/api/comments", vkHandler.ListComments)

	// Запуск сервера на порту 8080.
	if err := r.Run(":8080"); err != nil {
		log.Fatal("Failed to start server: ", err)
	}
}
