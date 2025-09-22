// Package database содержит инициализацию БД.
package database

import (
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// NewPostgresDB создает новое подключение к PostgreSQL.
func NewPostgresDB() (*gorm.DB, error) {
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		dsn = "host=localhost user=postgres password=postgres dbname=comments_analysis port=5432 sslmode=disable"
	}

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}
	return db, nil
}
