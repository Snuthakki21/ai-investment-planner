# Investment requirements and verification

| Requirement | Evidence |
|---|---|
| Exact dependency-constrained optimization | Initiative/FeasiblePortfolio/FeasibleSet/ExactOptimizer; original and independent decimal regressions. |
| Separate discounted selection | DiscountAssumptions and InvestmentAnalysis; independent manual NPV calculation test. |
| Explicit overlap control | OverlapPolicy; full-overlap, single-member and invalid shared-membership tests. |
| Revision-bound funding | FundingPolicy; accepted/stale criterion, stage order, dependency stage and full tranche tests. |
| Correlated scenario/regret analysis | SensitivityAssumptions; seeded reproducibility, nonnegative regret and zero-spread optimum tests. |
| Bounded AI interpretation | InvestmentBrief; existing person-month and unchanged-selection regression tests. |
| Visible workflow results | Funding memo UI displays both objectives, cash-flow table, stages and finite-policy regret. |
| Persistent workspace | app/platform tests and browser/native interaction checks. |

Execute `tests/test_ai_investment_planner.py`, `tests/test_ai_investment_planner_independent.py` and `tests/test_investment_product.py` plus the complete runtime/platform suite. Acceptance also requires a current static build, browser execution, public CI and an independent automated review of expanded source.
