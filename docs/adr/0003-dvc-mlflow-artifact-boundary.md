# ADR-0003: DVC / MLflow Artifact Boundary

## Status
Accepted

## Context
Both DVC and MLflow can version large binary artifacts and both can use
Azure Blob Storage as a backend. Without an explicit boundary, datasets and
trained models risk being duplicated, stored ambiguously, or tracked by the
wrong tool for their lifecycle needs.

## Decision
DVC owns datasets and reproducible data pipelines: raw data, processed/
feature data, and the `dvc.yaml` pipeline stages that transform one into the
other. Pointer files are Git-tracked; actual bytes live in an Azure Blob
container dedicated to DVC (e.g., `dvcstore`).

MLflow owns trained models and their lifecycle: run metadata (params,
metrics), the trained model artifact itself, and — critically — the
Model Registry stage (`Staging` / `Production` / `Archived`), which is what
the promotion/rollback mechanism (ADR-0002) operates on. MLflow's artifact
store points at a separate Azure Blob container (e.g., `mlflow-artifacts`),
physically distinct from DVC's, even though both are Azure Blob.

A trained model is never dual-tracked in both systems. Training scripts
(plain Git-tracked code) read DVC-tracked data and log to MLflow; they do
not decide the resulting model's registry stage — that is exclusively the
eval engine's responsibility (ADR-0002).

## Alternatives Considered
- **Single shared Azure Blob container for both tools**: saves minor initial
  setup effort, but prevents independent retention/access policies for raw
  data vs. model artifacts, and makes storage auditing ambiguous as the
  project grows.
- **Tracking trained models in DVC instead of MLflow**: loses MLflow's stage
  transition mechanism, which the entire canary promotion/rollback loop
  depends on.

## Consequences
- Clear, teachable rule: "reproducible pipeline lineage → DVC; serving
  stage/lifecycle → MLflow."
- Two separate Azure Blob containers to provision and manage instead of one.
- The eval engine has zero DVC dependency — it only ever talks to MLflow's
  Model Registry, keeping its responsibilities narrow (per ADR-0002).