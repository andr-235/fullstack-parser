package comments

import (
	"context"
	"errors"
	"io"
	"strings"
	"testing"

	"backend/internal/domain/comments"
	"backend/internal/domain/users"
	"backend/internal/repository"
	"backend/internal/repository/postgres"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockCommentRepository struct {
	mock.Mock
	postgres.CommentRepository
}

func (m *MockCommentRepository) Create(ctx context.Context, comment *comments.Comment) error {
	args := m.Called(ctx, comment)
	return args.Error(0)
}

func (m *MockCommentRepository) GetByID(ctx context.Context, id uuid.UUID) (*comments.Comment, error) {
	args := m.Called(ctx, id)
	return args.Get(0).(*comments.Comment), args.Error(1)
}

func (m *MockCommentRepository) Update(ctx context.Context, comment *comments.Comment) error {
	args := m.Called(ctx, comment)
	return args.Error(0)
}

func (m *MockCommentRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockCommentRepository) List(ctx context.Context, filters repository.ListFilters) ([]*comments.Comment, error) {
	args := m.Called(ctx, filters)
	return args.Get(0).([]*comments.Comment), args.Error(1)
}

func (m *MockCommentRepository) CountTotal(ctx context.Context) (int64, error) {
	args := m.Called(ctx)
	return args.Get(0).(int64), args.Error(1)
}

func (m *MockCommentRepository) CountAnalyzed(ctx context.Context) (int64, error) {
	args := m.Called(ctx)
	return args.Get(0).(int64), args.Error(1)
}

type MockUserRepository struct {
	mock.Mock
	postgres.UserRepository
}

func (m *MockUserRepository) GetByID(id uuid.UUID) (*users.User, error) {
	args := m.Called(id)
	return args.Get(0).(*users.User), args.Error(1)
}

func TestCommentsUseCase_CreateComment(t *testing.T) {
	mockCommentRepo := new(MockCommentRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(io.Discard)
	uc := NewCommentsUseCase(mockCommentRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	authorID := uuid.New()
	postID := uuid.New()
	validText := "Valid comment text"
	invalidShortText := ""
	invalidLongText := strings.Repeat("a", 1001)

	tests := []struct {
		name         string
		text         string
		authorID     uuid.UUID
		postID       *uuid.UUID
		setupMocks   func()
		expectedErr  string
	}{
		{
			name:       "success",
			text:       validText,
			authorID:   authorID,
			postID:     &postID,
			setupMocks: func() {
				mockUserRepo.On("GetByID", authorID).Return(&users.User{ID: authorID}, nil)
				mockCommentRepo.On("Create", ctx, mock.MatchedBy(func(c *comments.Comment) bool {
					return c.Text == validText && c.AuthorID == authorID && c.PostID != nil && !c.Analyzed
				})).Return(nil)
			},
		},
		{
			name:        "invalid short text",
			text:        invalidShortText,
			authorID:    authorID,
			postID:      &postID,
			setupMocks:  func() {},
			expectedErr: "текст комментария должен быть от 1 до 1000 символов",
		},
		{
			name:        "invalid long text",
			text:        invalidLongText,
			authorID:    authorID,
			postID:      &postID,
			setupMocks:  func() {},
			expectedErr: "текст комментария должен быть от 1 до 1000 символов",
		},
		{
			name:       "user not found",
			text:       validText,
			authorID:   authorID,
			postID:     &postID,
			setupMocks: func() {
				mockUserRepo.On("GetByID", authorID).Return(nil, gorm.ErrRecordNotFound)
			},
			expectedErr: gorm.ErrRecordNotFound.Error(),
		},
		{
			name:       "repo create error",
			text:       validText,
			authorID:   authorID,
			postID:     &postID,
			setupMocks: func() {
				mockUserRepo.On("GetByID", authorID).Return(&users.User{ID: authorID}, nil)
				mockCommentRepo.On("Create", mock.Anything, mock.Anything).Return(errors.New("db error"))
			},
			expectedErr: "db error",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.setupMocks()

			comment, err := uc.CreateComment(ctx, tt.text, tt.authorID, tt.postID)

			if tt.expectedErr != "" {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.expectedErr)
				assert.Nil(t, comment)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, comment)
				assert.Equal(t, validText, comment.Text)
				assert.Equal(t, authorID, comment.AuthorID)
				assert.False(t, comment.Analyzed)
			}

			mockUserRepo.AssertExpectations(t)
			mockCommentRepo.AssertExpectations(t)
		})
	}
}

func TestCommentsUseCase_GetComment(t *testing.T) {
	mockCommentRepo := new(MockCommentRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(io.Discard)
	uc := NewCommentsUseCase(mockCommentRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	id := uuid.New()
	expectedComment := &comments.Comment{ID: id, Text: "test", AuthorID: uuid.New(), Analyzed: false}

	tests := []struct {
		name        string
		id          uuid.UUID
		setupMocks  func()
		expectedErr string
	}{
		{
			name: "success",
			id:   id,
			setupMocks: func() {
				mockCommentRepo.On("GetByID", ctx, id).Return(expectedComment, nil)
			},
		},
		{
			name: "not found",
			id:   uuid.New(),
			setupMocks: func() {
				mockCommentRepo.On("GetByID", ctx, mock.Anything).Return(nil, gorm.ErrRecordNotFound)
			},
			expectedErr: gorm.ErrRecordNotFound.Error(),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.setupMocks()

			comment, err := uc.GetComment(ctx, tt.id)

			if tt.expectedErr != "" {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.expectedErr)
				assert.Nil(t, comment)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, expectedComment, comment)
			}

			mockCommentRepo.AssertExpectations(t)
		})
	}
}

func TestCommentsUseCase_UpdateComment(t *testing.T) {
	mockCommentRepo := new(MockCommentRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(io.Discard)
	uc := NewCommentsUseCase(mockCommentRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	id := uuid.New()
	currentUserID := uuid.New()
	validText := "Updated text"
	invalidText := ""
	comment := &comments.Comment{ID: id, Text: "old", AuthorID: currentUserID, Analyzed: false}
	wrongOwnershipComment := &comments.Comment{ID: id, Text: "old", AuthorID: uuid.New(), Analyzed: false}

	tests := []struct {
		name         string
		id           uuid.UUID
		text         string
		currentUserID uuid.UUID
		setupMocks   func()
		expectedErr  string
	}{
		{
			name:         "success",
			id:           id,
			text:         validText,
			currentUserID: currentUserID,
			setupMocks: func() {
				mockCommentRepo.On("GetByID", ctx, id).Return(comment, nil)
				mockCommentRepo.On("Update", ctx, mock.MatchedBy(func(c *comments.Comment) bool {
					return c.ID == id && c.Text == validText
				})).Return(nil)
			},
		},
		{
			name:         "invalid text",
			id:           id,
			text:         invalidText,
			currentUserID: currentUserID,
			setupMocks:   func() {},
			expectedErr:  "текст комментария должен быть от 1 до 1000 символов",
		},
		{
			name:         "not found",
			id:           uuid.New(),
			text:         validText,
			currentUserID: currentUserID,
			setupMocks: func() {
				mockCommentRepo.On("GetByID", ctx, mock.Anything).Return(nil, gorm.ErrRecordNotFound)
			},
			expectedErr: gorm.ErrRecordNotFound.Error(),
		},
		{
			name:         "no ownership",
			id:           id,
			text:         validText,
			currentUserID: uuid.New(),
			setupMocks: func() {
				mockCommentRepo.On("GetByID", ctx, id).Return(wrongOwnershipComment, nil)
			},
			expectedErr: "нет прав на выполнение операции с комментарием",
		},
		{
			name:         "repo update error",
			id:           id,
			text:         validText,
			currentUserID: currentUserID,
			setupMocks: func() {
				mockCommentRepo.On("GetByID", ctx, id).Return(comment, nil)
				mockCommentRepo.On("Update", mock.Anything, mock.Anything).Return(errors.New("update error"))
			},
			expectedErr: "update error",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.setupMocks()

			updatedComment, err := uc.UpdateComment(ctx, tt.id, tt.text, tt.currentUserID)

			if tt.expectedErr != "" {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.expectedErr)
				assert.Nil(t, updatedComment)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, updatedComment)
				assert.Equal(t, validText, updatedComment.Text)
			}

			mockCommentRepo.AssertExpectations(t)
		})
	}
}

func TestCommentsUseCase_DeleteComment(t *testing.T) {
	mockCommentRepo := new(MockCommentRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(io.Discard)
	uc := NewCommentsUseCase(mockCommentRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	id := uuid.New()
	currentUserID := uuid.New()
	comment := &comments.Comment{ID: id, AuthorID: currentUserID}
	wrongOwnershipComment := &comments.Comment{ID: id, AuthorID: uuid.New()}

	tests := []struct {
		name         string
		id           uuid.UUID
		currentUserID uuid.UUID
		setupMocks   func()
		expectedErr  string
	}{
		{
			name:         "success",
			id:           id,
			currentUserID: currentUserID,
			setupMocks: func() {
				mockCommentRepo.On("GetByID", ctx, id).Return(comment, nil)
				mockCommentRepo.On("Delete", ctx, id).Return(nil)
			},
		},
		{
			name:         "not found",
			id:           uuid.New(),
			currentUserID: currentUserID,
			setupMocks: func() {
				mockCommentRepo.On("GetByID", ctx, mock.Anything).Return(nil, gorm.ErrRecordNotFound)
			},
			expectedErr: gorm.ErrRecordNotFound.Error(),
		},
		{
			name:         "no ownership",
			id:           id,
			currentUserID: uuid.New(),
			setupMocks: func() {
				mockCommentRepo.On("GetByID", ctx, id).Return(wrongOwnershipComment, nil)
			},
			expectedErr: "нет прав на выполнение операции с комментарием",
		},
		{
			name:         "repo delete error",
			id:           id,
			currentUserID: currentUserID,
			setupMocks: func() {
				mockCommentRepo.On("GetByID", ctx, id).Return(comment, nil)
				mockCommentRepo.On("Delete", ctx, id).Return(errors.New("delete error"))
			},
			expectedErr: "delete error",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.setupMocks()

			err := uc.DeleteComment(ctx, tt.id, tt.currentUserID)

			if tt.expectedErr != "" {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.expectedErr)
			} else {
				assert.NoError(t, err)
			}

			mockCommentRepo.AssertExpectations(t)
		})
	}
}

func TestCommentsUseCase_ListComments(t *testing.T) {
	mockCommentRepo := new(MockCommentRepository)
	mockUserRepo := new(MockUserRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(io.Discard)
	uc := NewCommentsUseCase(mockCommentRepo, mockUserRepo, mockLogger)

	ctx := context.Background()
	filters := repository.ListFilters{Limit: 10, Offset: 0}
	expectedComments := []*comments.Comment{{ID: uuid.New(), Text: "test1"}, {ID: uuid.New(), Text: "test2"}}

	tests := []struct {
		name        string
		filters     repository.ListFilters
		setupMocks  func()
		expected    []*comments.Comment
		expectedErr string
	}{
		{
			name:    "success",
			filters: filters,
			setupMocks: func() {
				mockCommentRepo.On("List", ctx, filters).Return(expectedComments, nil)
			},
			expected: expectedComments,
		},
		{
			name:    "empty list",
			filters: filters,
			setupMocks: func() {
				mockCommentRepo.On("List", ctx, filters).Return([]*comments.Comment{}, nil)
			},
			expected: []*comments.Comment{},
		},
		{
			name:    "repo error",
			filters: filters,
			setupMocks: func() {
				mockCommentRepo.On("List", ctx, filters).Return(nil, errors.New("list error"))
			},
			expectedErr: "list error",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.setupMocks()

			commentsList, err := uc.ListComments(ctx, tt.filters)

			if tt.expectedErr != "" {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.expectedErr)
				assert.Nil(t, commentsList)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expected, commentsList)
			}

			mockCommentRepo.AssertExpectations(t)
		})
	}
}

func TestAnalysisUseCase_AnalyzeKeywords(t *testing.T) {
	mockRepo := new(MockCommentRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(io.Discard)
	uc := NewAnalysisUseCase(mockRepo, mockLogger)

	ctx := context.Background()
	id := uuid.New()
	commentTextWithKeywords := "This is about политика and экономика."
	commentTextNoKeywords := "Simple text."
	comment := &comments.Comment{ID: id, Text: commentTextWithKeywords, Analyzed: false}

	tests := []struct {
		name           string
		id             uuid.UUID
		setupMocks     func()
		expectedKeywords map[string]int
		expectedScore   float64
		expectedErr     string
	}{
		{
			name: "success with keywords",
			id:   id,
			setupMocks: func() {
				mockRepo.On("GetByID", ctx, id).Return(comment, nil)
				mockRepo.On("Update", ctx, mock.MatchedBy(func(c *comments.Comment) bool {
					return c.ID == id && c.Analyzed == true
				})).Return(nil)
			},
			expectedKeywords: map[string]int{"политика": 1, "экономика": 1},
			expectedScore:   2.0,
		},
		{
			name: "success no keywords",
			id:   id,
			setupMocks: func() {
				commentNoKw := &comments.Comment{ID: id, Text: commentTextNoKeywords, Analyzed: false}
				mockRepo.On("GetByID", ctx, id).Return(commentNoKw, nil)
				mockRepo.On("Update", ctx, mock.Anything).Return(nil)
			},
			expectedKeywords: map[string]int{},
			expectedScore:   0.0,
		},
		{
			name: "not found",
			id:   uuid.New(),
			setupMocks: func() {
				mockRepo.On("GetByID", ctx, mock.Anything).Return(nil, gorm.ErrRecordNotFound)
			},
			expectedErr: gorm.ErrRecordNotFound.Error(),
		},
		{
			name: "update error",
			id:   id,
			setupMocks: func() {
				mockRepo.On("GetByID", ctx, id).Return(comment, nil)
				mockRepo.On("Update", mock.Anything, mock.Anything).Return(errors.New("update error"))
			},
			expectedKeywords: map[string]int{"политика": 1, "экономика": 1},
			expectedScore:   2.0,
			expectedErr:     "update error",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.setupMocks()

			keywords, score, err := uc.AnalyzeKeywords(ctx, tt.id)

			if tt.expectedErr != "" {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.expectedErr)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expectedKeywords, keywords)
				assert.Equal(t, tt.expectedScore, score)
			}

			mockRepo.AssertExpectations(t)
		})
	}
}

func TestAnalysisUseCase_GetStats(t *testing.T) {
	mockRepo := new(MockCommentRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(io.Discard)
	uc := NewAnalysisUseCase(mockRepo, mockLogger)

	ctx := context.Background()
	total := int64(10)
	analyzed := int64(5)

	tests := []struct {
		name         string
		setupMocks   func()
		expected     map[string]int64
		expectedErr  string
	}{
		{
			name: "success",
			setupMocks: func() {
				mockRepo.On("CountTotal", ctx).Return(total, nil)
				mockRepo.On("CountAnalyzed", ctx).Return(analyzed, nil)
			},
			expected: map[string]int64{
				"total":      10,
				"analyzed":   5,
				"unanalyzed": 5,
			},
		},
		{
			name: "total count error",
			setupMocks: func() {
				mockRepo.On("CountTotal", ctx).Return(int64(0), errors.New("total error"))
			},
			expectedErr: "total error",
		},
		{
			name: "analyzed count error",
			setupMocks: func() {
				mockRepo.On("CountTotal", ctx).Return(total, nil)
				mockRepo.On("CountAnalyzed", ctx).Return(int64(0), errors.New("analyzed error"))
			},
			expectedErr: "analyzed error",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.setupMocks()

			stats, err := uc.GetStats(ctx)

			if tt.expectedErr != "" {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.expectedErr)
				assert.Nil(t, stats)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expected, stats)
			}

			mockRepo.AssertExpectations(t)
		})
	}
}