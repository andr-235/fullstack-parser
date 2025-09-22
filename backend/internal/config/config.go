package config

import (
  "github.com/go-playground/validator/v10"
  "github.com/spf13/viper"
)

// Config представляет структуру конфигурации приложения.
type Config struct {
  Server struct {
    Port string `mapstructure:"port" validate:"required"`
  } `mapstructure:"server"`

  Database struct {
    URL string `mapstructure:"url" validate:"required,uri"`
  } `mapstructure:"database"`

  Redis struct {
    URL string `mapstructure:"url" validate:"required,uri"`
  } `mapstructure:"redis"`

  JWT struct {
    Secret string `mapstructure:"secret" validate:"required,min=32"`
  } `mapstructure:"jwt"`

  Log struct {
    Level string `mapstructure:"level" validate:"oneof=debug info warn error"`
  } `mapstructure:"log"`
}

// LoadConfig загружает конфигурацию из файла yaml, с поддержкой env vars.
// path - путь к config.yaml.
func LoadConfig(path string) (*Config, error) {
  viper.SetConfigType("yaml")
  viper.SetConfigFile(path)

  if err := viper.ReadInConfig(); err != nil {
    return nil, err
  }

  viper.AutomaticEnv() // Позволяет переопределять через env vars

  cfg := &Config{}
  if err := viper.Unmarshal(cfg); err != nil {
    return nil, err
  }

  validate := validator.New()
  if err := validate.Struct(cfg); err != nil {
    return nil, err
  }

  return cfg, nil
}