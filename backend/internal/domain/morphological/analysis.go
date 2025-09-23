package morphological

import (
	"regexp"
)

// AnalysisResult represents the result of morphological analysis.
type AnalysisResult struct {
	Keywords  []string `json:"keywords"`
	Sentiment string   `json:"sentiment"`
}

// AnalyzeText performs placeholder morphological analysis on the given text.
// It extracts keywords using simple regex patterns for positive and negative words
// and determines sentiment based on the presence of those keywords.
// In a real implementation, this would use a proper NLP library like go-mystem or external service.
func AnalyzeText(text string) AnalysisResult {
	// Simple regex patterns for example Russian keywords (positive and negative)
	positiveRe := regexp.MustCompile(`\b(хорошо|отлично|позитив|любовь|класс|супер)\b`)
	negativeRe := regexp.MustCompile(`\b(плохо|ужасно|негатив|ненависть|отстой|фигня)\b`)

	// Extract matching keywords
	positiveKeywords := positiveRe.FindAllString(text, -1)
	negativeKeywords := negativeRe.FindAllString(text, -1)
	keywords := append(positiveKeywords, negativeKeywords...)

	// Determine sentiment based on keyword presence
	var sentiment string
	if len(positiveKeywords) > 0 {
		sentiment = "positive"
	} else if len(negativeKeywords) > 0 {
		sentiment = "negative"
	} else {
		sentiment = "neutral"
	}

	return AnalysisResult{
		Keywords:  keywords,
		Sentiment: sentiment,
	}
}