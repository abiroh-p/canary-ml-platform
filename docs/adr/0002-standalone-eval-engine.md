# ADR-0002: Evaluation Engine as a Standalone Service

## Status
Accepted

## Context
Something in the system must periodically read live metrics (latency, error
rate, prediction drift) for both stable and canary, apply a promotion/
rollback policy, and act on that decision by calling the gateway's admin API
and MLflow's stage transition API. This logic is stateful across evaluation
cycles (e.g., tracking consecutive failing checks) and depends on the Python
ecosystem (PromQL clients, numpy/scipy for drift math, the MLflow client).

## Decision
The evaluation engine is a standalone Python service: an independent process
running its own scheduling loop (wake up every N seconds, evaluate, sleep),
decoupled entirely from request-serving timing. It is a client of three
systems — Prometheus (reads metrics), the gateway's admin API (pushes split
decisions), and MLflow (reads/writes model registry stage) — and exposes no
business-logic API of its own (only a `/health` endpoint for Kubernetes
liveness probes).

## Alternatives Considered
- **Embedded in the Go gateway**: violates the gateway's data-plane-only
  design (ADR-0001) by adding PromQL queries, drift computation, and policy
  state to the hot-path process. Also forces Go to do statistical work
  Python's ecosystem handles natively.
- **Embedded in a model server**: layering violation — the model being
  evaluated should not also be the thing deciding whether it passes
  evaluation.

## Consequences
- Independent failure domain: if the eval engine crashes or a Prometheus
  query hangs, live request serving is unaffected.
- Independent scaling and deploy cadence from the gateway and model servers.
- Decisions lag reality by at most one evaluation interval — an accepted,
  expected eventual-consistency trade-off, not a bug.
- Requires the eval engine to be containerized/deployed as its own
  Kubernetes workload (a long-running Deployment, not a one-off Job, since
  it runs an internal scheduling loop rather than being externally
  triggered).