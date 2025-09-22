package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"os/signal"
	"syscall"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"github.com/prometheus/client_golang/prometheus"

	"github.com/hibiken/asynq"

	"backend/internal/config"
	"backend/internal/logger"
	"backend/internal/repository/redis"
	"backend/internal/usecase/comments"
	"backend/internal/usecase/morphological"
	"backend/internal/usecase/vk"
	"backend/internal/repository/tasks"
	"backend/internal/repository/postgres"
)

func main() {
	ctx := context.Background()
	cfg, err := config.NewConfig()
	if err != nil {
		log.Fatal("config error", err)
	}

	lg := logger.NewLogger()

	db, err := postgres.NewDB(cfg)
	if err != nil {
		log.Fatal("db error", err)
	}

	rdb := redis.NewRedisClient(cfg.RedisURL)
	defer rdb.Close()

	// DI for usecases - stub for now, assume implementations exist
	vkRepo, err := vk.NewVKRepository(cfg) // assume NewVKRepository from config or stub
	if err != nil {
		log.Fatal("vk repo error", err)
	}
	vkCommentsUC := vk.NewVKCommentsUseCase(vkRepo)

	commentRepo, err := comments.NewCommentRepository(db) // assume postgres impl
	if err != nil {
		log.Fatal("comment repo error", err)
	}
	commentUC := comments.NewCommentsUseCase(commentRepo)

	morphRepo := postgres.NewMorphologicalRepository(db, lg)
	morphUC := morphological.NewMorphologicalUseCase(commentRepo, morphRepo, lg)
	prometheus.MustRegister(morphUC.metrics)

	taskRepo := redis.NewTaskRepository(rdb)

	// Asynq worker
	worker := asynq.NewWorker("redis://localhost:6379", asynq.Config{Concurrency: 10})

	// Register handlers
	worker.Use(logger.NewAsynqHandler(lg)) // assume logger has Asynq handler or stub log

	worker.HandleFunc("vk:fetch_comments", func(ctx context.Context, t *asynq.Task) error {
		var payload struct {
			OwnerID string                 `json:"owner_id"`
			PostID  string                 `json:"post_id"`
			Options map[string]interface{} `json:"options"`
		}
		if err := json.Unmarshal(t.Payload(), &payload); err != nil {
			lg.Error("payload unmarshal error", err)
			return err
		}

		// Set status processing
		if err := taskRepo.SetStatus(ctx, t.ID(), tasks.StatusProcessing, nil); err != nil {
			lg.Error("set status error", err)
		}

		comments, err := vkCommentsUC.FetchComments(ctx, payload.OwnerID, payload.PostID, payload.Options)
		if err != nil {
			taskRepo.SetStatus(ctx, t.ID(), tasks.StatusFailed, map[string]interface{}{"error": err.Error()})
			return err
		}

		var commentIDs []uint
		// Save comments to DB via commentUC
		for _, comment := range comments {
			if err := commentUC.Create(ctx, comment); err != nil {
				lg.Error("comment create error", err)
			} else {
				commentIDs = append(commentIDs, comment.ID)
			}
		}

		// Enqueue process comments task
		processPayload, _ := json.Marshal(map[string]interface{}{"comment_ids": commentIDs})
		processTask, err := asynq.NewTask("vk:process_comments", processPayload)
		if err != nil {
			lg.Error("failed to create process task", err)
			return err
		}
		if _, err := taskRepo.Enqueue(processTask); err != nil {
			lg.Error("failed to enqueue process task", err)
			return err
		}

		// Set status completed with comment IDs
		taskRepo.SetStatus(ctx, t.ID(), tasks.StatusCompleted, map[string]interface{}{"comment_ids": commentIDs})
		return nil
	})

	worker.HandleFunc("vk:process_comments", func(ctx context.Context, t *asynq.Task) error {
		var payload struct {
			CommentIDs []uint `json:"comment_ids"`
		}
		if err := json.Unmarshal(t.Payload(), &payload); err != nil {
			lg.Error("payload unmarshal error", err)
			return err
		}

		// For batch, call AnalyzeBatch
		err := morphUC.AnalyzeBatch(ctx, payload.CommentIDs)
		if err != nil {
			taskRepo.SetStatus(ctx, t.ID(), tasks.StatusFailed, map[string]interface{}{"error": err.Error()})
			return err
		}

		// Update status
		taskRepo.SetStatus(ctx, t.ID(), tasks.StatusCompleted, nil)
		return nil
	})

	if err := worker.Run(); err != nil {
		log.Fatal("worker run error", err)
	}

	// Graceful shutdown
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	<-sig
	worker.Shutdown()
}