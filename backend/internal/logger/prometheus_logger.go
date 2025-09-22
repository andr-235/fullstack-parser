package logger

import (
	"context"
	"fmt"
	"time"

	"gorm.io/gorm/logger"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	gormQueryDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "gorm_query_duration_seconds",
			Help: "GORM query duration",
		},
		[]string{"operation"},
	)

	gormRowsAffected = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "gorm_rows_affected",
			Help: "Number of rows affected by GORM operation",
		},
		[]string{"operation"},
	)

	commentAnalysisDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "comment_analysis_duration_seconds",
			Help: "Duration of comment analysis",
		},
		[]string{"type"},
	)
)

// getCorrelationID extracts correlation ID from gin context
func getCorrelationID(ctx context.Context) string {
	if ginCtx, exists := ctx.Value(gin.ContextKey).(*gin.Context); exists {
		if id, ok := ginCtx.Get("correlation_id"); ok {
			if strID, ok := id.(string); ok {
				return strID
			}
		}
	}
	return "unknown"
}

// PrometheusLogger for GORM
type PrometheusLogger struct {
	logger.Config
}

// NewPrometheusLogger creates new GORM logger with Prometheus metrics
func NewPrometheusLogger() logger.Interface {
	return &PrometheusLogger{
		Config: logger.Config{
			LogLevel:                  logger.Info,
			SlowThreshold:             time.Second,
			Colorful:                  true,
			IgnoreRecordNotFoundError: false,
		},
	}
}

// LogMode sets log level
func (l *PrometheusLogger) LogMode(level logger.LogLevel) logger.Interface {
	l.Config.LogLevel = level
	return l
}

// Info logs info message
func (l *PrometheusLogger) Info(ctx context.Context, s string, args ...interface{}) {
	if l.Config.LogLevel <= logger.Info {
		id := getCorrelationID(ctx)
		fmt.Printf("[%s] INFO: %s\n", id, fmt.Sprintf(s, args...))
	}
}

// Warn logs warning message
func (l *PrometheusLogger) Warn(ctx context.Context, s string, args ...interface{}) {
	if l.Config.LogLevel <= logger.Warn {
		id := getCorrelationID(ctx)
		fmt.Printf("[%s] WARN: %s\n", id, fmt.Sprintf(s, args...))
	}
}

// Error logs error message
func (l *PrometheusLogger) Error(ctx context.Context, s string, args ...interface{}) {
	if l.Config.LogLevel <= logger.Error {
		id := getCorrelationID(ctx)
		fmt.Printf("[%s] ERROR: %s\n", id, fmt.Sprintf(s, args...))
	}
}

// Trace implements logger.Interface for GORM tracing
func (l *PrometheusLogger) Trace(ctx context.Context, begin time.Time, fc func() (string, int64), err error) {
	var rows int64
	if l.Config.LogLevel <= logger.Info {
		id := getCorrelationID(ctx)
		sql := ""
		if fc != nil {
			sql, rows = fc()
		}
		fmt.Printf("[%s] %s SQL: %s rows: %d error: %v\n", id, begin.Format("2006/01/02 15:04:05"), sql, rows, err)
	} else if fc != nil {
		_, rows = fc()
	}

	duration := time.Since(begin).Seconds()
	gormQueryDuration.WithLabelValues("query").Observe(duration)
	if rows > 0 {
		gormRowsAffected.WithLabelValues("query").Observe(float64(rows))
	}
}

// ObserveCommentAnalysis observes duration for comment analysis
func ObserveCommentAnalysis(ctx context.Context, duration float64, analysisType string) {
	commentAnalysisDuration.WithLabelValues(analysisType).Observe(duration)
}
