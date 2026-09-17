# Investment contracts

## Objective definitions

Original adjusted annual benefit is `benefit_k × benefit_factor × confidence × (1 − risk)`. Original net value subtracts implementation cost. A feasible set must include all dependencies and fit budget and person-month capacity. Empty selection has zero value. Only positive value is funded; equal positive value favors lower cost.

For the discounted alternative, apply overlap deductions to adjusted annual benefit. For year `t`, benefit is multiplied by `(1 + growth)^(t − 1)`, annual operating cost is `implementation cost × operating-cost fraction`, and the net flow is discounted by `(1 + discount rate)^t`. Subtract implementation cost at time zero. No terminal value, tax effect, inflation adjustment or financing structure is assumed.

Overlap deduction is `fraction × (sum of selected group benefits − maximum selected group benefit)`. The deduction is zero with fewer than two selected members. Groups are nonoverlapping by initiative membership.

## Funding evidence schema

```json
{
  "initiative": "data-foundation",
  "stage": "discovery",
  "assumption_revision": "64 lowercase hexadecimal characters from the current report",
  "metric": "Synthetic pilot acceptance rate",
  "observed": 95,
  "target": 90,
  "operator": ">=",
  "source_reference": "Original synthetic acceptance fixture",
  "reviewer": "Example committee reviewer"
}
```

The above revision text is explanatory; copy the actual SHA-256 digest from `details.funding_evidence.assumption_revision`. Accepted stages release modeled incremental fractions: discovery 0.10, pilot 0.30, scale 0.60. Allowed statuses are evidence_missing, stale_revision, previous_stage_incomplete, dependency_stage_incomplete, criterion_failed and evidence_accepted. Both `>=` and `<=` are supported. Duplicate initiative/stage records are rejected.

The digest includes budget, capacity, benefit factor, initiatives, declared DCF options and overlap groups. Evidence and random seed do not alter this funding-assumption identity. Changing a material assumption requires new evidence. Source references and reviewer names are unverified scenario fields; nothing here authenticates a funding approval or moves money.

## Sensitivity

The older report uses 500 independent triangular draws for the original selection. The expanded report uses 20–500 seeded Gaussian common-factor paths, a latent correlation from zero to one and spread from zero to one. Benefit multipliers are clipped to [0,3] and converted to Decimal. Correlation describes latent factors before clipping and does not promise the same correlation of final cash flows.

Candidate policies comprise the original choice, discounted choice, no funding and top eight base-NPV feasible sets, deduplicated. Regret is the difference from the best displayed candidate on each path. Tied best policies each receive a best-in-path count. Results are synthetic assumption sensitivity, not observed ROI, calibrated forecasts or globally optimal future decisions.

## Failure behavior

Validate all core and expanded fields before calling a provider. Unknown dependency, dependency cycle, duplicate initiative, malformed overlap, invalid evidence digest, duplicate gate, invalid rates, nonfinite values and unsupported bounds fail explicitly. No partial funding approval is returned on invalid input.
