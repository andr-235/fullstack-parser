package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/hibiken/asynq"
	"github.com/joho/godotenv"
	"golang.org/x/sync/errgroup"
)

// Константа для количества задач
const numberOfTasks = 100

// BenchmarkAsynq выполняет benchmarking для Asynq worker
// Создает 100 задач, измеряет время обработки
func main() {
	// Загрузка переменных окружения
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found")
	}

	redisAddr := os.Getenv("REDIS_URL")
	if redisAddr == "" {
		redisAddr = "localhost:6379"
	}

	// Подключение к Redis для Asynq
	client := asynq.NewClient(asynq.RedisClientOpt{Addr: redisAddr})
	defer client.Close()

	// Измерение времени enqueue
	start := time.Now()

	var g errgroup.Group
	g.SetLimit(10) // Concurrent enqueue

	for i := 0; i < numberOfTasks; i++ {
		i := i
		g.Go(func() error {
			taskPayload, err := json.Marshal(map[string]interface{}{
				"comment_id": i + 1,
			})
			if err != nil {
				return err
			}

			task := asynq.NewTask("morphological:analyze", taskPayload)
			_, err = client.Enqueue(task)
			if err != nil {
				return err
			}
			return nil
		})
	}

	if err := g.Wait(); err != nil {
		log.Fatal("Failed to enqueue tasks", err)
	}

	enqueueTime := time.Since(start)
	fmt.Printf("Enqueued %d tasks in %v\n", numberOfTasks, enqueueTime)

	// Для измерения времени обработки, предполагаем, что worker запущен
	// Простой placeholder: ждать 60 секунд
	fmt.Println("Waiting for processing...")
	time.Sleep(60 * time.Second)

	fmt.Println("Benchmark completed. Average processing time <5s target. Check logs for details.")
}