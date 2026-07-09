# Architecture Decision Records

This directory contains the Architecture Decision Records (ADRs) for the
canary-ml-platform project. Each ADR captures one significant architectural
decision: the context that forced it, the options considered, and the
consequences accepted.

## Process

- ADRs are numbered sequentially (`0001`, `0002`, ...) and never renumbered.
- Once a decision is Accepted, its file is not edited to change the decision
  itself. If a decision changes later, a new ADR is written and marked as
  superseding the old one; the old ADR's Status is updated to
  `Superseded by ADR-000X`.
- Use `template.md` as the starting point for any new ADR.

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](0001-traffic-split-control-plane.md) | Traffic split control plane design | Accepted |
| [0002](0002-standalone-eval-engine.md) | Evaluation engine as a standalone service | Accepted |
| [0003](0003-dvc-mlflow-artifact-boundary.md) | DVC / MLflow artifact boundary | Accepted |
| [0004](0004-psi-drift-detection.md) | PSI for prediction drift detection | Accepted |