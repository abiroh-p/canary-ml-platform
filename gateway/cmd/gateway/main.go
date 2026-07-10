package main

import (
	"log/slog"
	"net/http"
	"os"
	"strconv"

	"github.com/abiroh-p/canary-ml-platform/gateway/internal/config"
	"github.com/abiroh-p/canary-ml-platform/gateway/internal/control"
	"github.com/abiroh-p/canary-ml-platform/gateway/internal/logging"
	"github.com/abiroh-p/canary-ml-platform/gateway/internal/router"
)

func main() {
	logging.Configure("INFO")

	cfg, err := config.Load()
	if err != nil {
		slog.Error("failed to load config", "error", err)
		os.Exit(1)
	}

	splitState := control.NewSplitState()

	rt, err := router.New(cfg.StableUpstreamURL, cfg.CanaryUpstreamURL, splitState)
	if err != nil {
		slog.Error("failed to create router", "error", err)
		os.Exit(1)
	}

	errCh := make(chan error, 2)

	go func() {
		addr := ":" + strconv.Itoa(cfg.Port)
		slog.Info("data plane listening", "addr", addr)
		errCh <- http.ListenAndServe(addr, rt)
	}()

	go func() {
		addr := ":" + strconv.Itoa(cfg.AdminPort)
		slog.Info("control plane listening", "addr", addr)
		errCh <- http.ListenAndServe(addr, control.AdminHandler(splitState))
	}()

	err = <-errCh
	slog.Error("server exited", "error", err)
	os.Exit(1)
}
