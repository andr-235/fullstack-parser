package logger

import (
	"fmt"
	"time"

	"gorm.io/gorm/logger"
	"gorm.io/gorm/utils"

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
)

// PrometheusLogger for GORM
type PrometheusLogger struct {
	logger.Config
}

// NewPrometheusLogger создает новый logger для GORM с Prometheus metrics
func NewPrometheusLogger() logger.Interface {
	return &PrometheusLogger{}
}

// LogMode returns the log mode
func (l *PrometheusLogger) LogMode(level logger.LogLevel) logger.Interface {
	l.Config.LogLevel = level
	return l
}

// Info implements logger.Interface
func (l *PrometheusLogger) Info(ctx context.Context, s string, args ...interface{}) {
	fmt.Printf(s, args...)
}

// Warn implements logger.Interface
func (l *PrometheusLogger) Warn(ctx context.Context, s string, args ...interface{}) {
	fmt.Printf(s, args...)
}

// Error implements logger.Interface
func (l *PrometheusLogger) Error(ctx context.Context, s string, args ...interface{}) {
	fmt.Printf(s, args...)
}

// Trace implements logger.Interface
func (l *PrometheusLogger) Trace(ctx context.Context, begin, end time.Time, fields ...interface{}) {
	if l.Config.LogLevel <= logger.Trace {
		fmt.Printf("%s [%s] %s", begin.Format("2006/01/02 15:04:05"), end.Format("2006/01/02 15:04:05"), utils.FileWithLineNum())
		for i := 0; i < len(fields); i += 2 {
			fmt.Printf(" %v = %v", fields[i], fields[i+1])
		}
		fmt.Println()
	}

	duration := end.Sub(begin).Seconds()
	gormQueryDuration.WithLabelValues("trace").Observe(duration)
}