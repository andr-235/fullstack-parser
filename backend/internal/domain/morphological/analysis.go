package morphological

// TextRequest представляет структуру запроса для анализа текста.
type TextRequest struct {
	Text string `json:"text" binding:"required"`
}

// AnalysisResult представляет результат морфологического анализа текста.
type AnalysisResult struct {
	Words   []string            `json:"words"`
	Lemmas  []string            `json:"lemmas"`
	PosTags map[string]string   `json:"pos_tags"`
}