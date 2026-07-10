// Package router implements the gateway's data plane: routes each
// inference request to the stable or canary model-server based on the
// current SplitState, and forwards the response back to the client.
package router

import (
	"log/slog"
	"math/rand"
	"net/http"
	"net/http/httputil"
	"net/url"
	"time"

	"github.com/abiroh-p/canary-ml-platform/gateway/internal/control"
)

type Router struct {
	stableProxy *httputil.ReverseProxy
	canaryProxy *httputil.ReverseProxy
	splitState  *control.SplitState
}

func New(stableURL, canaryURL string, splitState *control.SplitState) (*Router, error) {
	stableTarget, err := url.Parse(stableURL)
	if err != nil {
		return nil, err
	}
	canaryTarget, err := url.Parse(canaryURL)
	if err != nil {
		return nil, err
	}

	return &Router{
		stableProxy: httputil.NewSingleHostReverseProxy(stableTarget),
		canaryProxy: httputil.NewSingleHostReverseProxy(canaryTarget),
		splitState:  splitState,
	}, nil
}

func (rt *Router) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	start := time.Now()

	weight := rt.splitState.CanaryWeight()
	useCanary := int32(rand.Intn(100)) < weight

	target := "stable"
	proxy := rt.stableProxy
	if useCanary {
		target = "canary"
		proxy = rt.canaryProxy
	}

	proxy.ServeHTTP(w, r)

	latencyMs := float64(time.Since(start).Milliseconds())
	RequestsTotal.WithLabelValues(target).Inc()
	RequestLatency.WithLabelValues(target).Observe(latencyMs)

	slog.Info("request routed",
		"target", target,
		"canary_weight", weight,
		"latency_ms", latencyMs,
	)
}