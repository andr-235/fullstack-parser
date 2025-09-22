package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/stretchr/testify/assert"
)

func TestPrometheusMiddleware(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := httptest.NewRecorder()
	req := httptest.NewRequest("GET", "/test", nil)

	c, _ := gin.CreateTestContext(r)
	c.Request = req

	// Call middleware
	mw := PrometheusMiddleware()
	mw(c)

	assert.Equal(t, http.StatusOK, r.Code)

	// Check metrics
	// Note: Metrics are global, so we can't assert exact values easily in unit test
	// This test verifies the middleware runs without error
}

func TestPrometheusMiddleware_MultipleRequests(t *testing.T) {
	gin.SetMode(gin.TestMode)

	for i := 0; i < 3; i++ {
		r := httptest.NewRecorder()
		req := httptest.NewRequest("POST", "/api/tasks", nil)

		c, _ := gin.CreateTestContext(r)
		c.Request = req

		mw := PrometheusMiddleware()
		mw(c)
	}

	// Verify metrics were incremented (basic check)
	requestsTotal := httpRequestsTotal.WithLabelValues("POST", "/api/tasks", "200")
	assert.Greater(t, prometheus.SummaryVec{}.Collect()[0].Observed, float64(0))
}