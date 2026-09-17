# Independent automated Staff Engineer review — expanded application

Review date: 2026-09-17. A separate automated reviewer, independent of the product author, examined the current expanded source. This is an automated engineering review, not an external human audit or production certification.

## Scope and method

Read the current product diff, product requirements, actual domain/application/AI services, compatibility adapter, product UI template and author tests. Independently designed adverse-input tests in `tests/test_product_review.py` and rendering tests in `tests/product-review-ui.test.mjs`. The product author corrected implementation findings; the reviewer retested those changes.

This domain review excludes an independent audit of shared persistence/HTTP code, distribution packaging, hosted CI and live-browser visual quality. The whole existing Python suite was executed for regression evidence; that execution does not expand the source-review scope. Live provider accuracy and real financial outcomes were not measured.

## Verdict

**Pass for the documented product scope after independent verification. No unresolved implementation finding was reproduced in this review.** The verdict applies to the attached source snapshot and executed checks. It does not assert a defect-free or production-certified system.

## Requirements and architecture assessment

The six domain requirements: exact bounded optimization; separate DCF objective; overlap deductions; revision-bound staged evidence; declared correlated sensitivity; bounded narrative interpretation.

Initiative and FeasiblePortfolio are typed Decimal-valued entities. FeasibleSet and ExactOptimizer enforce dependency/budget/capacity constraints. DiscountAssumptions and OverlapPolicy define a separate discounted objective; FundingEvidence and FundingPolicy enforce current revisions and sequential/dependency stages. InvestmentAnalysis adds a disclosed finite-candidate correlated regret analysis. The original and discounted objectives remain separately labeled.

New results are calculated by the domain services, rendered in the product-specific template and included in full downloadable reports. Independent UI checks confirm all published scenarios render without undefined or NaN values, preserve result evidence and escape hostile labels. Common workspace actions are assessed separately.

## Findings and resolution

No supported domain defect was found. Independent tests challenge an independent small-universe DCF oracle, reversed dependency ordering, stale overlap evidence, explicit no-funding choice and nested input immutability.

## Executed verification

- Full Python suite: 138 tests, zero failures, 2 explicit skips.
- Independent domain regressions: 5 passed as part of that run.
- Static build: the standalone product and all declared examples built successfully.
- Frontend and independent product UI tests: 34 total, 28 passed, 6 explicit absent-project skips, zero failures. Three checks specifically exercise the expanded UI.

```sh
python3 -m unittest discover -s tests
python3 -m portfolio build --output dist
node --test --test-timeout=20000 tests/frontend.test.mjs tests/product-review-ui.test.mjs
```

## Source snapshot

[Machine-readable SHA-256 snapshot](STAFF_REVIEW_V2_SOURCE.json) identifies every reviewed domain module, compatibility adapter, template, independent test and current requirement document. Future material edits require renewed review of changed behavior.

| File | SHA-256 |
|---|---|
| `app/ai/__init__.py` | `89de0ae138526f75b093dfba123bdab0083c03f9cc42eaf8c18c364ddc9204cb` |
| `app/ai/brief.py` | `544bf4aa8d917818eec12b83147201db04e81555fa7c8887ec7be88c633a2917` |
| `app/application/__init__.py` | `7f7ac1bcd2e479c4e455c451c564b9dea9c49a02e7acc56e1f7e77f250b9a8d7` |
| `app/application/product.py` | `04c62445a77b2ac7d066bdce04cde90e4af07b73527423ad57226787f5b5a30b` |
| `app/domain/__init__.py` | `eaf555ce5a3cc48b684b3dbb2e01af922636fdd24f1399bcdc7b733961533bcd` |
| `app/domain/analysis.py` | `e8f7ae4d0f5e39bfe702d063b3b5fcd138673c1e2d8868c22d891cfca96822cb` |
| `app/domain/funding.py` | `7b39ded5da952ec88bec4f96be06a353accb2970eba79887edeb777d9282f236` |
| `app/domain/optimization.py` | `cd4fcf3f8f7144692b866f1fc17579df4b3fd5b2047cc53af58f550e542f5716` |
| `app/domain/sensitivity.py` | `77bab8c89dc6b561cf696b36eb36635e166f023504107322aa533335bf33f6f3` |
| `app/domain/validation.py` | `40a204bd1a917b23dc64df76a3e04b3fa1ec218a8d8b99affe119e2d444046e6` |
| `app/domain/valuation.py` | `2168bd722bee14a8a2c9ebfabd3b8073d36a82df745f1c9aff55fd9bb8a61568` |
| `docs/PRODUCT.md` | `3df11517cc5b97d389b5ede349d2ea2a594b71ca8d76848137b6caebee1fb9b2` |
| `docs/REQUIREMENTS.md` | `66b5293e0324dce9a548f377ba6f3bff87a19ea96ce11ac20a07c67647bac6ea` |
| `projects/ai_investment_planner/project.py` | `87cc8db9d435791b3c96836c9fcdbeba1eae1fa63d332d80aadc99dc03e1715c` |
| `tests/product-review-ui.test.mjs` | `fa6cd2f0715d0ec4032cbe22c54f9f24a5e6089b79a32939d1414e878437193d` |
| `tests/test_product_review.py` | `01d4197ac525807e461eb65bc07caf63af4e70bca0d1ed0bb8b6235dca95d9f4` |
| `web/templates/ai_investment_planner.js` | `b1ad29691ec896e67b47e84d2e3384f6452dfc55ed8aa1c19d1de03fc025f5b2` |
