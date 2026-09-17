# Independent automated Staff Engineer review

**Reviewer:** Non-authoring portfolio-strategy agent. **Scope:** the complete project README, `project.py`, author tests and independent regression tests; the reviewer did not implement this application. **Method:** Source inspection, contract comparison, existing test inspection and three independently constructed executable reproductions. This is an automated engineering review, not human financial-model validation.

**Final code verdict: PASS after author remediation.** Four reproduced correctness/contract failures were reported before remediation and retained below for traceability. The reviewer independently verified each correction. The completed README was subsequently checked against the implementation and accurately describes the bounded algorithm, units, assumptions, AI seam and operational limits. Frontend behavior and final standalone packaging remain separate validation scopes.

## Findings

### P2 — Rounding the incumbent can select the worse investment

`optimize()` stores its winning `net_value_k` rounded to three decimals, then compares the next unrounded net value against that rounded number. With a budget and capacity of one, two mutually exclusive initiatives each cost one and require one month. Their benefits are 1.1004 and 1.1003, confidence is one and risk is zero. The implementation selects the second, lower-benefit initiative because the first incumbent was rounded down.

Expected: choose `better`. Observed: `worse`. Preserve the full-precision comparison value throughout enumeration and round only the reported presentation. Add a regression that checks the selected set, not merely the rounded net figure.

### P2 — Binary floating-point costs exclude an exactly affordable set

Two initiatives cost 0.1 and 0.2 ($k), each offers benefit one, and the budget is 0.3 with capacity two. Both are mathematically feasible, but the sum of binary floats exceeds 0.3. The implementation funds only the first, although both create more net value.

Expected: select both. Observed: select `first` only. Use decimal monetary inputs or explicit scaled units for feasibility; test the exact budget boundary.

### P2 — Non-object payload escapes the advertised input error boundary

`run(None)` reaches `validate()` and raises `AttributeError` on `.get()`. The common project contract specifies `ValueError` for unsupported input, and the shared CLI catches that type for a controlled error. Add the root-object guard before copying/reading the input and test null, arrays and strings.

### P2 — Funding-frontier labels differed from the actual feasibility budget

For base budget 0.3, the 125% scenario was solved at 0.375 but reported `budget_k: 0.38`. A single initiative costing 0.377 was excluded despite appearing affordable under the displayed figure. The author now calculates the scenario budget using Decimal multiplication and passes exactly the same resulting value to the optimizer and report. Independent regression observes 0.375, rejects 0.377 and accepts 0.374. This fourth finding is closed.

## Reproductions

The reviewer executed each input directly against `run()` in a clean Python invocation. Output at the initial checkpoint:

```text
Rounded incumbent: selected=['worse'], reported net_value_k=0.1
Exact budget: selected=['first'], cost_k=0.1
Null input: AttributeError: 'NoneType' object has no attribute 'get'
```

The existing eight tests cover ordinary feasibility, a large-gap optimum, no positive value, cycles, missing dependencies, nonfinite budgets, changed budgets and seeded repeatability. They did not cover these precision or root-schema failures. All three findings are independently reproducible without live models or external data.

## Architecture and scope observations

The bounded exhaustive search is appropriate for at most sixteen initiatives. Dependency closure and topological delivery waves are explicit. Optional AI writes a narrative over calculated selection; it does not choose the portfolio. Inputs and benefit spreads are clearly labeled illustrative. The model subtracts one-time cost from adjusted annual benefit without discounting and uses independent triangular draws; those are documented planning assumptions, not calibrated valuation or confidence intervals.

## Remediation verification

The author now converts monetary/optimization assumptions using Decimal(str(value)), retains exact incumbent comparisons, rounds only reported presentation values, and rejects non-object root payloads with ValueError. Independent tests verify the original two selection failures, an additional small positive improvement, and null/array/string input boundaries. All seven independent tests and all eight author tests passed on 2026-09-17 (exit code 0):

```sh
python3 -m unittest tests.test_ai_investment_planner tests.test_ai_investment_planner_independent -v
```

The original reproductions now select `better`, select both `first` and `second`, and raise controlled `ValueError`, respectively. The reviewer did not edit the implementation. All four P2 findings are closed for this source version.

Reviewed project.py SHA-256: `fdced9d38f1677587aa0da2f570dac29497649a18889afd95f4c4562a0bf431f`.

Independent test module SHA-256: `daf2975004fe22e224c26967f5b8e4a97a6bf63f96dd069660ef8a4df48c5094`.

This is not human financial-model validation, live-model evaluation, frontend review or a deployment approval. Financial assumptions remain illustrative; the model does not establish observed ROI.


The final independent additions also reject malformed initiative shapes and verify that the model receives `effort_person_months` rather than an ambiguous `months` selection field, while the computed allocation remains unchanged. That test validates the model input contract using a controlled double; it does not establish the factuality of generated prose. The coordinator reported a real Ollama smoke test separately in docs/MODEL_INTEGRATION.md. The review does not turn that transport result into a general model-quality claim.

Final integrated verification: 338 tests passed and 99.70% combined statement/branch coverage across the staging source; this module measured 100%. Standalone repositories must repeat their included test/build checks after export. README examples/frontend commands target those generated standalone assets.
