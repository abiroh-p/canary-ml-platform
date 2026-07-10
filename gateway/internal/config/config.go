// Package config holds gateway configuration, sourced from environment
// variables. Single source of truth — no other package should call
// os.Getenv directly.
package config

import (
	"fmt"
	"os"
	"strconv"
)

type Config struct {
	Port              int
	StableUpstreamURL string
	CanaryUpstreamURL string
	AdminPort         int
}

func Load() (*Config, error) {
	port, err := getEnvInt("GATEWAY_PORT", 8080)
	if err != nil {
		return nil, err
	}
	adminPort, err := getEnvInt("GATEWAY_ADMIN_PORT", 8081)
	if err != nil {
		return nil, err
	}

	cfg := &Config{
		Port:              port,
		StableUpstreamURL: getEnvStr("STABLE_UPSTREAM_URL", "http://localhost:8001"),
		CanaryUpstreamURL: getEnvStr("CANARY_UPSTREAM_URL", "http://localhost:8002"),
		AdminPort:         adminPort,
	}
	return cfg, nil
}

func getEnvStr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func getEnvInt(key string, fallback int) (int, error) {
	v := os.Getenv(key)
	if v == "" {
		return fallback, nil
	}
	n, err := strconv.Atoi(v)
	if err != nil {
		return 0, fmt.Errorf("invalid value for %s: %w", key, err)
	}
	return n, nil
}