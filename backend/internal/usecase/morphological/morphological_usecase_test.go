package morphological

import (
	"errors"
	"testing"

	"backend/internal/domain/morphological"

	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockMorphologyService struct {
	mock.Mock
}

func (m *MockMorphologyService) AnalyzeText(text string) (*morphological.AnalysisResult, error) {
	args := m.Called(text)
	return args.Get(0).(*morphological.AnalysisResult), args.Error(0)
}

type MockMorphologicalRepository struct {
	mock.Mock
}

func (m *MockMorphologicalRepository) SaveResult(textHash string, result *morphological.AnalysisResult) error {
	args := m.Called(textHash, result)
	return args.Error(0)
}

func TestMorphologicalUsecase_AnalyzeText_Success(t *testing.T) {
	mockService := new(MockMorphologyService)
	mockRepo := new(MockMorphologicalRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewMorphologicalUsecase(mockService, mockRepo, mockLogger)

	text := "test text"
	expectedResult := &morphological.AnalysisResult{Words: []string{"test"}}
	mockService.On("AnalyzeText", text).Return(expectedResult, nil)
	mockRepo.On("SaveResult", mock.Anything, expectedResult).Return(nil)

	result, err := uc.AnalyzeText(&morphological.TextRequest{Text: text})

	assert.NoError(t, err)
	assert.Equal(t, expectedResult, result)
	mockService.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
}

func TestMorphologicalUsecase_AnalyzeText_InvalidText(t *testing.T) {
	mockService := new(MockMorphologyService)
	mockRepo := new(MockMorphologicalRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewMorphologicalUsecase(mockService, mockRepo, mockLogger)

	_, err := uc.AnalyzeText(&morphological.TextRequest{Text: ""})

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "текст не может быть пустым")
	mockService.AssertNotCalled(t, "AnalyzeText")
}

func TestMorphologicalUsecase_AnalyzeText_ServiceError(t *testing.T) {
	mockService := new(MockMorphologyService)
	mockRepo := new(MockMorphologicalRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewMorphologicalUsecase(mockService, mockRepo, mockLogger)

	text := "test text"
	mockService.On("AnalyzeText", text).Return(nil, errors.New("service error"))

	_, err := uc.AnalyzeText(&morphological.TextRequest{Text: text})

	assert.Error(t, err)
	assert.Equal(t, "service error", err.Error())
	mockRepo.AssertNotCalled(t, "SaveResult")
}

func TestMorphologicalUsecase_ValidateText_Success(t *testing.T) {
	mockService := new(MockMorphologyService)
	mockRepo := new(MockMorphologicalRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewMorphologicalUsecase(mockService, mockRepo, mockLogger)

	err := uc.ValidateText("valid text")

	assert.NoError(t, err)
}

func TestMorphologicalUsecase_ValidateText_Empty(t *testing.T) {
	mockService := new(MockMorphologyService)
	mockRepo := new(MockMorphologicalRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewMorphologicalUsecase(mockService, mockRepo, mockLogger)

	err := uc.ValidateText("")

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "текст не может быть пустым")
}

func TestMorphologicalUsecase_GetTextHash(t *testing.T) {
	mockService := new(MockMorphologyService)
	mockRepo := new(MockMorphologicalRepository)
	mockLogger := logrus.New()
	mockLogger.SetOutput(nil)

	uc := NewMorphologicalUsecase(mockService, mockRepo, mockLogger)

	hash := uc.GetTextHash("test text")

	assert.NotEmpty(t, hash)
	assert.Len(t, hash, 10) // Expected length from hashText
}