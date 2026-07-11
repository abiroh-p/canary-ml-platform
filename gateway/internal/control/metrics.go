package control

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var CanaryWeightGauge = promauto.NewGauge(prometheus.GaugeOpts{
	Name: "gateway_canary_weight_percent",
	Help: "Current canary traffic split percentage (0-100)",
})
