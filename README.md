# canary-ml-platform

A production-style ML model serving platform that routes live inference
traffic between a stable and a canary model version, continuously evaluates
the canary using latency, error rate, and prediction-drift metrics, and
automatically promotes or rolls back the canary based on configurable
policy — with no manual intervention required.

This project is not "train a model and deploy it." It's the infrastructure
layer that decides, safely and automatically, whether a new model version
is trustworthy enough to serve more traffic.
## Architecture

```text
                           +------------------+
                           |      Client      |
                           +--------+---------+
                                    |
                                    v
                     +-------------------------------+
                     | API Gateway (Go, REST/gRPC)   |
                     +---------------+---------------+
                                     |
                                     v
                     +-------------------------------+
                     | Traffic Router (Weighted Split)|
                     |         95% / 5%              |
                     +---------------+---------------+
                                     |
                 +-------------------+-------------------+
                 |                                       |
                 v                                       v
      +-----------------------+              +-----------------------+
      | Model Server v1       |              | Model Server v2       |
      | Stable                |              | Canary                |
      +-----------+-----------+              +-----------+-----------+
                  |                                      |
                  +-------------------+------------------+
                                      |
                                      v
                  +--------------------------------------+
                  | Monitoring & Evaluation Engine       |
                  | • Latency                            |
                  | • Error Rate                         |
                  | • Prediction Drift (PSI)             |
                  +------------------+-------------------+
                                     |
                                     v
                       +-------------------------------+
                       | Model Registry (MLflow)       |
                       +---------------+---------------+
                                       |
                        Promote / Rollback Decision
                                       |
                                       v
                     Updates Traffic Split Automatically
```

## Why this design

Every non-trivial architectural decision in this project — why Go for the
gateway, why the evaluation engine is a standalone service, how traffic
splitting works without adding request latency, how model artifacts are
versioned, how drift is measured — is written up as an Architecture
Decision Record in [`docs/adr/`](docs/adr/README.md). Start there for the
reasoning behind the code.

## Tech stack

| Layer | Technology |
|---|---|
| API Gateway | Go, gRPC (internal), REST (external) |
| Model Serving | FastAPI, scikit-learn / XGBoost |
| Evaluation Engine | Python, PSI-based drift detection |
| Model Registry | MLflow |
| Data Versioning | DVC (Azure Blob backend) |
| Monitoring | Prometheus, Grafana |
| Deployment | Docker, Kubernetes (Azure Kubernetes Service) |
| CI/CD | GitHub Actions |

## Status

🚧 **Early / actively being built.** Architecture and repository structure
are in place; services are not yet implemented. This README will gain setup
and run instructions as each piece becomes real — see
[`docs/adr/`](docs/adr/README.md) for what's been decided so far.

## Repository layout

| Directory | Contents |
|---|---|
| `gateway/` | Go API gateway — routing, traffic split control plane |
| `model-server/` | FastAPI inference service |
| `eval-engine/` | Standalone evaluation/policy service (drift, promote/rollback) |
| `training/` | Model training scripts |
| `data/` | DVC-tracked dataset pointers |
| `infra/` | Docker Compose, Kubernetes manifests |
| `monitoring/` | Prometheus config, Grafana dashboards |
| `docs/` | Architecture Decision Records and design docs |