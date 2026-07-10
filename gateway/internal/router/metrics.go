package router

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	RequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "gateway_requests_total",
			Help: "Total requests routed, labeled by target",
		},
		[]string{"target"},
	)

	RequestLatency = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "gateway_request_latency_ms",
			Help:    "Request latency in milliseconds, labeled by target",
			Buckets: []float64{5, 10, 25, 50, 100, 250, 500, 1000},
		},
		[]string{"target"},
	)
)