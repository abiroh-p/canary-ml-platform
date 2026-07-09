# ADR-0004: PSI for Prediction Drift Detection

## Status
Accepted

## Context
The evaluation engine needs a quantitative way to determine whether the
canary model's live predictions differ meaningfully from the stable model's,
using only data already flowing through the system (no separate training-time
reference dataset pipeline, which would be significant added scope). The
chosen method must yield a graduated magnitude, not just a binary flag, so
policy can make decisions like "hold at current traffic %" as well as clear
promote/rollback calls.

## Decision
The eval engine computes the Population Stability Index (PSI) between the
stable model's and canary model's predicted score distributions, over a
rolling recent window. The stable model's distribution is treated as
"expected"; the canary's as "actual." Bins are quantile-based, derived from
the stable distribution, fixed at 10 bins for determinism. Standard industry
thresholds apply: PSI < 0.1 = healthy, 0.1–0.25 = hold, > 0.25 = rollback.
PSI is recomputed every evaluation cycle, never treated as a one-time check.

This is prediction drift (canary vs. stable, on live traffic), not full data
drift (live traffic vs. training-time distribution) — the latter is
explicitly out of scope for now (see Consequences).

## Alternatives Considered
- **Jensen-Shannon divergence**: information-theoretically cleaner and
  symmetric, but PSI's 0.1/0.25 thresholds are more widely recognized
  (originating from credit-risk/fraud score monitoring, a close analogue to
  monitoring live model scores) and immediately interpretable without
  additional justification.
- **Kolmogorov-Smirnov test**: gives a significance flag (yes/no at a
  confidence level) rather than a magnitude score, and becomes
  oversensitive at high traffic volume, flagging operationally meaningless
  differences as significant. Not a good fit for a graduated policy.

## Consequences
- Requires model servers to log prediction scores somewhere the eval engine
  can read them, in addition to Prometheus (which is better suited to
  numeric metrics/counters than raw score distributions) — a requirement to
  design into the model server, not yet specified.
- Simple enough (~20 lines: binning + summation formula) to implement from
  scratch rather than depending on a monitoring library, keeping every line
  explainable.
- True feature-level data drift (vs. training-time distribution) is
  explicitly deferred as a Phase 2 / future-work item, not built now.