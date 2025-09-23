package postgres

import (
	"context"
	"testing"
	"time"

	"vk-analyzer/internal/domain/comments"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/suite"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type IntegrationTestSuite struct {
	suite.Suite
	db          *gorm.DB
	container   testcontainers.Container
	commentRepo CommentRepository
}

func (suite *IntegrationTestSuite) SetupSuite() {
	// Запуск PostgreSQL контейнера
	ctx := context.Background()
	req := testcontainers.ContainerRequest{
		Image:        "postgres:15-alpine",
		ExposedPorts: []string{"5432/tcp"},
		Env: map[string]string{
			"POSTGRES_PASSWORD": "testpass",
			"POSTGRES_USER":     "testuser",
			"POSTGRES_DB":       "testdb",
		},
		WaitingFor: wait.ForLog("database system is ready to accept connections").
			WithOccurrence(2).WithStartupTimeout(5 * time.Second),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	suite.Require().NoError(err)
	suite.container = container

	// Получение порта контейнера
	host, err := container.Host(ctx)
	suite.Require().NoError(err)
	port, err := container.MappedPort(ctx, "5432")
	suite.Require().NoError(err)

	// Подключение к базе данных
	dsn := "host=" + host + " user=testuser password=testpass dbname=testdb port=" + port.Port() + " sslmode=disable TimeZone=UTC"
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	suite.Require().NoError(err)
	suite.db = db

	// Автомиграция
	err = db.AutoMigrate(&comments.Comment{})
	suite.Require().NoError(err)

	// Создание репозитория
	suite.commentRepo = NewCommentRepository(db)
}

func (suite *IntegrationTestSuite) TearDownSuite() {
	if suite.container != nil {
		suite.container.Terminate(context.Background())
	}
}

func (suite *IntegrationTestSuite) SetupTest() {
	// Очистка данных перед каждым тестом
	suite.db.Exec("DELETE FROM comments")
}

func TestIntegrationTestSuite(t *testing.T) {
	suite.Run(t, new(IntegrationTestSuite))
}

func (suite *IntegrationTestSuite) TestCreateMany_Success() {
	// Arrange
	testComments := []comments.Comment{
		{
			ID:     1,
			FromID: 12345,
			Date:   time.Now().Unix(),
			Text:   "Test comment 1",
			Likes:  &comments.Likes{Count: 10},
		},
		{
			ID:     2,
			FromID: 67890,
			Date:   time.Now().Unix(),
			Text:   "Test comment 2",
			Likes:  &comments.Likes{Count: 5},
		},
	}

	// Act
	err := suite.commentRepo.CreateMany(testComments)

	// Assert
	assert.NoError(suite.T(), err)

	// Проверка что комментарии созданы
	var count int64
	suite.db.Model(&comments.Comment{}).Count(&count)
	assert.Equal(suite.T(), int64(2), count)
}

func (suite *IntegrationTestSuite) TestCreateMany_EmptySlice() {
	// Arrange
	testComments := []comments.Comment{}

	// Act
	err := suite.commentRepo.CreateMany(testComments)

	// Assert
	assert.NoError(suite.T(), err)

	// Проверка что комментарии не созданы
	var count int64
	suite.db.Model(&comments.Comment{}).Count(&count)
	assert.Equal(suite.T(), int64(0), count)
}

func (suite *IntegrationTestSuite) TestGetByID_Success() {
	// Arrange
	testComment := comments.Comment{
		ID:     1,
		FromID: 12345,
		Date:   time.Now().Unix(),
		Text:   "Test comment",
		Likes:  &comments.Likes{Count: 10},
	}
	suite.db.Create(&testComment)

	// Act
	result, err := suite.commentRepo.GetByID(1)

	// Assert
	assert.NoError(suite.T(), err)
	assert.NotNil(suite.T(), result)
	assert.Equal(suite.T(), int64(1), result.ID)
	assert.Equal(suite.T(), int64(12345), result.FromID)
	assert.Equal(suite.T(), "Test comment", result.Text)
	assert.Equal(suite.T(), 10, result.Likes)
}

func (suite *IntegrationTestSuite) TestGetByID_NotFound() {
	// Act
	result, err := suite.commentRepo.GetByID(999)

	// Assert
	assert.Error(suite.T(), err)
	assert.Nil(suite.T(), result)
	assert.Equal(suite.T(), gorm.ErrRecordNotFound, err)
}

func (suite *IntegrationTestSuite) TestUpdate_Success() {
	// Arrange
	testComment := comments.Comment{
		ID:     1,
		FromID: 12345,
		Date:   time.Now().Unix(),
		Text:   "Original text",
		Likes:  &comments.Likes{Count: 10},
	}
	suite.db.Create(&testComment)

	// Act
	testComment.Text = "Updated text"
	testComment.Likes = &comments.Likes{Count: 20}
	err := suite.commentRepo.Update(&testComment)

	// Assert
	assert.NoError(suite.T(), err)

	// Проверка что комментарий обновлен
	var updatedComment comments.Comment
	suite.db.First(&updatedComment, 1)
	assert.Equal(suite.T(), "Updated text", updatedComment.Text)
	assert.Equal(suite.T(), 20, updatedComment.Likes)
}

func (suite *IntegrationTestSuite) TestUpdate_NotFound() {
	// Arrange
	testComment := &comments.Comment{
		ID:     999,
		FromID: 12345,
		Date:   time.Now().Unix(),
		Text:   "Non-existent comment",
		Likes:  &comments.Likes{Count: 10},
	}

	// Act
	err := suite.commentRepo.Update(testComment)

	// Assert
	assert.Error(suite.T(), err)
}

func (suite *IntegrationTestSuite) TestConcurrentAccess() {
	// Arrange
	testComments := make([]comments.Comment, 100)
	for i := 0; i < 100; i++ {
		testComments[i] = comments.Comment{
			ID:     int64(i + 1),
			FromID: int64(1000 + i),
			Date:   time.Now().Unix(),
			Text:   "Concurrent comment " + string(rune(i)),
			Likes:  &comments.Likes{Count: i},
		}
	}

	// Act - параллельное создание
	done := make(chan bool, 2)
	go func() {
		suite.commentRepo.CreateMany(testComments[:50])
		done <- true
	}()
	go func() {
		suite.commentRepo.CreateMany(testComments[50:])
		done <- true
	}()

	// Ожидание завершения
	<-done
	<-done

	// Assert
	var count int64
	suite.db.Model(&comments.Comment{}).Count(&count)
	assert.Equal(suite.T(), int64(100), count)
}

func (suite *IntegrationTestSuite) TestDatabaseConnectionFailure() {
	// Arrange - закрываем соединение
	sqlDB, _ := suite.db.DB()
	sqlDB.Close()

	// Act
	err := suite.commentRepo.CreateMany([]comments.Comment{
		{ID: 1, Text: "Test"},
	})

	// Assert
	assert.Error(suite.T(), err)
}

func (suite *IntegrationTestSuite) TestTransactionRollback() {
	// Arrange
	testComments := []comments.Comment{
		{
			ID:     1,
			FromID: 12345,
			Date:   time.Now().Unix(),
			Text:   "Valid comment",
			Likes:  &comments.Likes{Count: 10},
		},
		{
			ID:     1, // Дубликат ID - вызовет ошибку
			FromID: 67890,
			Date:   time.Now().Unix(),
			Text:   "Invalid comment",
			Likes:  &comments.Likes{Count: 5},
		},
	}

	// Act
	err := suite.commentRepo.CreateMany(testComments)

	// Assert
	assert.Error(suite.T(), err)

	// Проверка что ни один комментарий не создан
	var count int64
	suite.db.Model(&comments.Comment{}).Count(&count)
	assert.Equal(suite.T(), int64(0), count)
}

func (suite *IntegrationTestSuite) TestLargeDataSet() {
	// Arrange - создание большого набора данных
	testComments := make([]comments.Comment, 1000)
	for i := 0; i < 1000; i++ {
		testComments[i] = comments.Comment{
			ID:     int64(i + 1),
			FromID: int64(10000 + i),
			Date:   time.Now().Unix(),
			Text:   "Large dataset comment " + string(rune(i%26+'A')),
			Likes:  &comments.Likes{Count: i % 100},
		}
	}

	// Act
	start := time.Now()
	err := suite.commentRepo.CreateMany(testComments)
	duration := time.Since(start)

	// Assert
	assert.NoError(suite.T(), err)
	assert.True(suite.T(), duration < 5*time.Second, "Large dataset should be inserted within 5 seconds")

	// Проверка что все комментарии созданы
	var count int64
	suite.db.Model(&comments.Comment{}).Count(&count)
	assert.Equal(suite.T(), int64(1000), count)
}
