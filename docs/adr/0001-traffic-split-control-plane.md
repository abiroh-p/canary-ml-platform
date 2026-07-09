# ADR-0001: Traffic Split Control Plane Design

## Status
Accepted

## Context
The gateway must know, on every incoming request, what percentage of traffic
to send to the canary model vs. the stable model. This value changes over
time as the evaluation engine promotes or rolls back the canary. The gateway
sits on the hot path, so reading this value must not add latency or an
external dependency to request handling.

## Decision
The gateway exposes an admin API (`POST /admin/traffic-split`) that accepts
a new canary weight. The gateway holds the current split in memory, safe for
concurrent access (via `sync/atomic` or a `sync.RWMutex`-protected struct),
and every inference request reads this in-memory value directly — no I/O in
the hot path. The evaluation engine is the only caller of this admin API.

This establishes a clear control-plane / data-plane split: the admin API and
the eval engine's decision loop form the control plane (can be slow, can do
complex logic); the per-request routing path is the data plane (must stay
fast, must never block on an external call).

## Alternatives Considered
- **Polling a config file or database on an interval**: introduces
  unpredictable lag between decision and effect, and redundant reads under
  high request volume unless cached — which just reinvents the in-memory
  cache we're building anyway, with added latency.
- **Kubernetes ConfigMap + watch**: couples the gateway's core routing logic
  to running inside Kubernetes specifically, hurting local development
  (Docker Compose) and testability. Also reintroduces watch/poll latency via
  a different substrate.

## Consequences
- Zero added latency on the request path from split-lookup.
- The gateway's internal state must be designed for safe concurrent
  read/write from the start (many goroutines reading, one rare writer).
- The gateway works identically in Docker Compose locally and in AKS later,
  with no Kubernetes-specific code.
- If the gateway process restarts, the in-memory split resets to a default
  (e.g., 0% canary) until the eval engine's next cycle re-pushes the current
  value — this is an accepted trade-off; the alternative (persisting split
  state externally) adds a dependency we don't need for this project's scope.