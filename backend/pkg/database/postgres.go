// Package database содержит инициализацию БД.
package database

import (
	"gorm.io/gorm"
	"gorm.io/driver/postgres"

	"backend/config"
)

// NewPostgresDB создает новое подключение к PostgreSQL.
func NewPostgresDB() (*gorm.DB, error) {
	dsn := config.GetDSN()
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}
	return db, nil
}