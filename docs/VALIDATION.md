# Standalone verification evidence

Checked at 2026-09-17T05:01:53.393529+00:00. These results come from commands executed inside this repository after export.

Runtime versions: Python 3.14.7; Node.js v25.9.0.

Standalone release verification: **PASS**. All recorded commands passed.

| Check | Observed result |
|---|---|
| Python unit and integration tests | 74 discovered; 72 executed; 2 skipped |
| Statement coverage | 496/501 (99.00%) |
| Branch coverage | 228/234 (97.44%) |
| Frontend tests | 31 discovered; 25 executed; 6 skipped |
| Built application discovery | ai_investment_planner |
| Installed project directories | ai_investment_planner |
| Installed UI templates | ai_investment_planner |
| Missing README targets | [] |
| Default input | Executed through the repository CLI; saved in `examples/report.json` |

Reproduce from the repository root:

```sh
python -m pip install -r requirements-dev.txt
python -m coverage run -m unittest discover -s tests -v
python -m coverage report --fail-under=90
python -m portfolio build --output dist
node --test tests/frontend.test.mjs
```

Application source SHA-256: `fdced9d38f1677587aa0da2f570dac29497649a18889afd95f4c4562a0bf431f`.

Coverage includes this application and its shared Python runtime. Skipped tests exercise capabilities belonging to applications absent from this standalone repository. Provider transport tests use controlled doubles; these counts are not live-model accuracy measurements. The frontend suite exercises rendering, escaping, input binding and asynchronous state with controlled DOM/worker harnesses; it is not an exhaustive visual, accessibility or browser compatibility audit. Coverage measures executed code paths and does not establish semantic correctness.

See the solution-specific independent review linked in the README and the [shared runtime review](INDEPENDENT_RUNTIME_REVIEW.md) for review findings, repairs and limits.
