"""Public adapter for the modular investment application."""
from app.domain.validation import number, validate
from app.domain.optimization import optimize
from app.application.product import ProductApplication

def default_input():
    return {
        "budget_k": 340, "capacity_months": 20, "benefit_factor": 1.0, "seed": 21,
        "discounted_cash_flow": {"horizon_years": 3, "discount_rate": .10, "annual_benefit_growth": 0, "annual_operating_cost_fraction": .08},
        "benefit_overlaps": [], "stage_evidence": [],
        "correlated_sensitivity": {"paths": 100, "correlation": .60, "spread": .30},
        "initiatives": [
            {"id": "data-foundation", "name": "Trusted data foundation", "cost_k": 90, "months": 5, "benefit_k": 125, "confidence": 0.85, "risk": 0.1, "depends_on": [], "owner": "Data Platform"},
            {"id": "test-data", "name": "Synthetic testing service", "cost_k": 110, "months": 6, "benefit_k": 260, "confidence": 0.8, "risk": 0.15, "depends_on": ["data-foundation"], "owner": "Engineering Enablement"},
            {"id": "incident", "name": "Incident investigation assistant", "cost_k": 75, "months": 4, "benefit_k": 155, "confidence": 0.75, "risk": 0.2, "depends_on": [], "owner": "Operations"},
            {"id": "policy", "name": "Grounded policy search", "cost_k": 65, "months": 4, "benefit_k": 145, "confidence": 0.85, "risk": 0.15, "depends_on": ["data-foundation"], "owner": "Knowledge Services"},
            {"id": "autonomous", "name": "Autonomous remediation", "cost_k": 170, "months": 10, "benefit_k": 470, "confidence": 0.4, "risk": 0.65, "depends_on": ["incident"], "owner": "Operations"},
        ],
    }

def run(payload, context=None):
    return ProductApplication().run(payload, context)

_tight = default_input()
_tight["budget_k"] = 150
_stress = default_input()
_stress["benefit_factor"] = 0.5
META = {
    "id": "ai_investment_planner", "title": "AI Investment Planner", "order": 10, "flagship": False,
    "category": "Leadership", "buyer": "Director of Engineering / Business Sponsor",
    "question": "Which AI initiatives deserve funding and delivery capacity?",
    "promise": "Make funding choices and their assumptions visible.",
    "description": "An exact portfolio optimizer with dependency constraints, benefit sensitivity, accountable owners and staged delivery gates.",
    "principal": "Separates trusted calculations from optional model narrative; makes constraints and uncertainty inspectable.",
    "director": "Connects funding, capacity, dependencies, benefit assumptions and accountable delivery owners.",
    "patterns": ["Constrained optimization", "Sensitivity analysis", "Grounded executive brief"],
    "architecture": ["Validate initiative assumptions", "Resolve dependencies", "Enumerate feasible portfolios", "Stress-test benefit assumptions", "Assign owner and evidence gates", "Optionally draft a model brief"],
    "risks": ["Optimistic benefit assumptions", "Double-counted benefits", "Correlated delivery failures"],
    "limits": ["Financial inputs are illustrative, not observed ROI.", "Exact solver is bounded to 16 initiatives.", "Person-month capacity is not a calendar schedule; independent benefit draws are not calibrated confidence intervals."],
    "demo_inputs": [{"label": "Base investment case", "payload": default_input()}, {"label": "Tighter budget", "payload": _tight}, {"label": "Benefits fall by half", "payload": _stress}],
}

from app.domain.funding import assumption_revision as _assumption_revision
_staged = default_input()
_staged["discounted_cash_flow"] = {"horizon_years": 3, "discount_rate": .10, "annual_benefit_growth": 0, "annual_operating_cost_fraction": .08}
_staged["benefit_overlaps"] = [{"name": "shared operational effort", "members": ["incident", "autonomous"], "overlap_fraction": .65}]
_staged["stage_evidence"] = [{"initiative": "data-foundation", "stage": "discovery", "assumption_revision": _assumption_revision(_staged), "metric": "Synthetic pilot acceptance rate", "observed": 95, "target": 90, "operator": ">=", "source_reference": "Original synthetic pilot fixture", "reviewer": "Example committee reviewer"}]
META["demo_inputs"].append({"label": "Review staged evidence and discounted value", "payload": _staged})
