package integration

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/hibiken/asynq"
	"github.com/stretchr/testify/suite"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"vk-analyzer/internal/delivery/http/handlers/vk"
	"vk-analyzer/internal/usecase/vk"
	"vk-analyzer/internal/domain/comments"
)

type VKFlowIntegrationTestSuite struct {
	suite.Suite
	postgresContainer testcontainers.Container
	redisContainer   testcontainers.Container
	db               *gorm.DB
	server           *httptest.Server
	taskID           string
}

func (suite *VKFlowIntegrationTestSuite) SetupSuite() {
	// Start PostgreSQL container
	ctx := context.Background()
	postgresReq := testcontainers.ContainerRequest{
		Image:        "postgres:15-alpine",
		ExposedPorts: []string{"5432/tcp"},
		Env: map[string]string{
			"POSTGRES_PASSWORD": "testpass",
			"POSTGRES_USER":     "testuser",
			"POSTGRES_DB":       "testdb",
		},
		WaitingFor: wait.ForLog("database system is ready to accept connections").
			WithOccurrence(2).WithStartupTimeout(30 * time.Second),
	}

	postgresContainer, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: postgresReq,
		Started:          true,
	})
	suite.Require().NoError(err)
	suite.postgresContainer = postgresContainer

	// Start Redis container
	redisReq := testcontainers.ContainerRequest{
		Image:        "redis:7-alpine",
		ExposedPorts: []string{"6379/tcp"},
		WaitingFor:   wait.ForLog("Ready to accept connections").WithStartupTimeout(30 * time.Second),
	}

	redisContainer, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: redisReq,
		Started:          true,
	})
	suite.Require().NoError(err)
	suite.redisContainer = redisContainer

	// Get ports
	postgresPort, err := postgresContainer.MappedPort(ctx, "5432")
	suite.Require().NoError(err)
	redisPort, err := redisContainer.MappedPort(ctx, "6379")
	suite.Require().NoError(err)

	host, err := postgresContainer.Host(ctx)
	suite.Require().NoError(err)
	redisHost, err := redisContainer.Host(ctx)
	suite.Require().NoError(err)

	// Connect to PostgreSQL
	dsn := fmt.Sprintf("host=%s user=testuser password=testpass dbname=testdb port=%s sslmode=disable TimeZone=UTC", host, postgresPort.Port())
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	suite.Require().NoError(err)
	suite.db = db

	// AutoMigrate
	err = db.AutoMigrate(&comments.Comment{})
	suite.Require().NoError(err)

	// Setup Gin router with test use case (mocked for integration)
	uc := vk.NewVKCommentsUseCase()
	h := vk.NewVKHandler(uc)
	r := gin.Default()
	r.POST("/api/vk/fetch-comments", h.FetchComments)
	r.GET("/api/vk/task/:task_id", h.TaskStatus)
	r.GET("/api/comments", h.ListComments)
	suite.server = httptest.NewServer(r)
}

func (suite *VKFlowIntegrationTestSuite) TearDownSuite() {
	suite.server.Close()
	if suite.postgresContainer != nil {
		suite.postgresContainer.Terminate(context.Background())
	}
	if suite.redisContainer != nil {
		suite.redisContainer.Terminate(context.Background())
	}
}

func (suite *VKFlowIntegrationTestSuite) TestFullFlow_Success() {
	// Arrange - Prepare test data
	body := []byte(`{"owner_id":-123,"post_id":456}`)
	req, err := http.NewRequest("POST", "/api/vk/fetch-comments", bytes.NewReader(body))
	suite.Require().NoError(err)

	// Act - Send request to fetch comments
	w := httptest.NewRecorder()
	suite.server.ServeHTTP(w, req)

	// Assert - Check response
	assert.Equal(suite.T(), http.StatusOK, w.Code)
	var resp map[string]interface{}
	json.NewDecoder(w.Body).Decode(&resp)
	taskID := resp["task_id"].(string)
	suite.taskID = taskID
	assert.NotEmpty(suite.T(), taskID)

	// Act - Check task status
	statusReq, _ := http.NewRequest("GET", fmt.Sprintf("/api/vk/task/%s", taskID), nil)
	statusW := httptest.NewRecorder()
	suite.server.ServeHTTP(statusW, statusReq)

	// Assert - Status should be completed (placeholder)
	var statusResp map[string]interface{}
	json.NewDecoder(statusW.Body).Decode(&statusResp)
	assert.Equal(suite.T(), "completed", statusResp["status"])

	// Act - List comments
	listReq, _ := http.NewRequest("GET", "/api/comments?task_id="+taskID+"&limit=10", nil)
	listW := httptest.NewRecorder()
	suite.server.ServeHTTP(listW, listReq)

	// Assert - Comments should be available
	var comments []comments.Comment
	json.NewDecoder(listW.Body).Decode(&comments)
	assert.Len(suite.T(), comments, 10)
	assert.Equal(suite.T(), taskID, comments[0].TaskID)
}

func (suite *VKFlowIntegrationTestSuite) TestFullFlow_Failure() {
	// Arrange - Invalid request to trigger error
	body := []byte(`{"owner_id":"invalid","post_id":456}`)
	req, _ := http.NewRequest("POST", "/api/vk/fetch-comments", bytes.NewReader(body))

	// Act
	w := httptest.NewRecorder()
	suite.server.ServeHTTP(w, req)

	// Assert
	assert.Equal(suite.T(), http.StatusBadRequest, w.Code)
	var resp map[string]interface{}
	json.NewDecoder(w.Body).Decode(&resp)
	assert.Contains(suite.T(), resp["error"], "Invalid request body")
}

func (suite *VKFlowIntegrationTestSuite) TestTaskStatus_EmptyTaskID() {
	// Arrange - Empty task ID
	req, _ := http.NewRequest("GET", "/api/vk/task/", nil)

	// Act
	w := httptest.NewRecorder()
	suite.server.ServeHTTP(w, req)

	// Assert
	assert.Equal(suite.T(), http.StatusBadRequest, w.Code)
	var resp map[string]interface{}
	json.NewDecoder(w.Body).Decode(&resp)
	assert.Equal(suite.T(), "Task ID is required", resp["error"])
}

func (suite *VKFlowIntegrationTestSuite) TestListComments_InvalidLimit() {
	// Arrange - Invalid limit param
	req, _ := http.NewRequest("GET", "/api/comments?limit=invalid", nil)

	// Act
	w := httptest.NewRecorder()
	suite.server.ServeHTTP(w, req)

	// Assert
	assert.Equal(suite.T(), http.StatusBadRequest, w.Code)
	var resp map[string]interface{}
	json.NewDecoder(w.Body).Decode(&resp)
	assert.Contains(suite.T(), resp["error"], "Invalid limit")
}

func TestVKFlowIntegrationTestSuite(t *testing.T) {
	suite.Run(t, new(VKFlowIntegrationTestSuite))
}
