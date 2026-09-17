# Investment product runbook

1. Load a scenario and confirm budget units (USD thousands) and effort units (person-months).
2. Validate initiative ownership, dependencies and benefit assumptions. Save the scenario revision.
3. Execute and compare original net-value and discounted selections. Investigate differences before selecting an objective for a decision.
4. Inspect overlap deductions and correlated sensitivity. Record which assumptions require a measured business baseline.
5. Copy the current assumption revision into stage-evidence records only after the corresponding evidence is available. Specify a source, metric, threshold and reviewer label. These remain scenario data, not authenticated approval.
6. Rerun and inspect missing, stale, failed and dependency-blocked gates. Export the input and report together.
7. Save execution comparisons and review rationale in the workspace. Revisit evidence when assumptions change.

## Troubleshooting

| Symptom | Check |
|---|---|
| No initiatives selected | Every feasible set may have nonpositive adjusted value or fail budget/capacity/dependencies. |
| Discounted choice differs | Horizon, discount, operating cost and overlap semantics differ from the original objective. |
| Evidence is stale | Recreate evidence against the current assumption digest; do not relabel old observations blindly. |
| Pilot/scale is blocked | Complete earlier stages and the same stage for dependencies. |
| Total eligible funding is below committed cost | Only accepted evidence contributes to incremental modeled tranches. |
| Correlated uncertainty seems optimistic | Inputs are declared sensitivities, not calibrated distributions. Validate spread and shared downside assumptions. |
| A model brief describes calendar months | Reject that interpretation; effort is person-months. The solver report remains the source of fact. |

Run domain and full application tests after changes. Regenerate examples and request a new independent source review before claiming expanded coverage. Preserve prior reports with their source identities; a historical review is not evidence for later code.

Browser-local and native SQLite workspaces are separate. Export browser data before clearing its origin storage and back up native workspace state before migration. The native server remains a local single-operator deployment unless authentication is explicitly implemented.
