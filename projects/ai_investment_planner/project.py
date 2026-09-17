"""Dependency-aware investment selection over transparent synthetic assumptions."""
from __future__ import annotations
import copy
import math
import random
from decimal import Decimal


def default_input():
    return {
        "budget_k": 340, "capacity_months": 20, "benefit_factor": 1.0, "seed": 21,
        "initiatives": [
            {"id": "data-foundation", "name": "Trusted data foundation", "cost_k": 90, "months": 5, "benefit_k": 125, "confidence": 0.85, "risk": 0.1, "depends_on": [], "owner": "Data Platform"},
            {"id": "test-data", "name": "Synthetic testing service", "cost_k": 110, "months": 6, "benefit_k": 260, "confidence": 0.8, "risk": 0.15, "depends_on": ["data-foundation"], "owner": "Engineering Enablement"},
            {"id": "incident", "name": "Incident investigation assistant", "cost_k": 75, "months": 4, "benefit_k": 155, "confidence": 0.75, "risk": 0.2, "depends_on": [], "owner": "Operations"},
            {"id": "policy", "name": "Grounded policy search", "cost_k": 65, "months": 4, "benefit_k": 145, "confidence": 0.85, "risk": 0.15, "depends_on": ["data-foundation"], "owner": "Knowledge Services"},
            {"id": "autonomous", "name": "Autonomous remediation", "cost_k": 170, "months": 10, "benefit_k": 470, "confidence": 0.4, "risk": 0.65, "depends_on": ["incident"], "owner": "Operations"},
        ],
    }


def number(value, field, low=0, high=1e7):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high or (isinstance(value, float) and not math.isfinite(value)):
        raise ValueError(f"{field} must be finite and between {low} and {high}")
    return value


def validate(payload):
    if not isinstance(payload, dict):
        raise ValueError("Input must be an object")
    data = copy.deepcopy(payload)
    for name in ("budget_k", "capacity_months", "benefit_factor"):
        number(data.get(name), name, 0, 100000 if name != "benefit_factor" else 3)
    initiatives = data.get("initiatives")
    if not isinstance(initiatives, list) or not 1 <= len(initiatives) <= 16:
        raise ValueError("Provide 1 to 16 initiatives for exact bounded optimization")
    ids = set()
    for item in initiatives:
        if not isinstance(item, dict):
            raise ValueError("Every initiative must be an object")
        for field in ("id", "name", "owner"):
            if not isinstance(item.get(field), str) or not 1 <= len(item[field]) <= 100:
                raise ValueError(f"Each initiative needs a short {field}")
        if item["id"] in ids:
            raise ValueError("Initiative identifiers must be unique")
        ids.add(item["id"])
        for field in ("cost_k", "months", "benefit_k"):
            number(item.get(field), field, 0, 100000)
        for field in ("confidence", "risk"):
            number(item.get(field), field, 0, 1)
        if not isinstance(item.get("depends_on"), list) or not all(isinstance(x, str) for x in item["depends_on"]):
            raise ValueError("Dependencies must be a list of identifiers")
    graph = {item["id"]: set(item["depends_on"]) for item in initiatives}
    if any(deps - ids for deps in graph.values()):
        raise ValueError("Unknown dependency")
    visited, visiting = set(), set()
    def walk(node):
        if node in visiting:
            raise ValueError("Dependency cycle detected")
        if node in visited:
            return
        visiting.add(node)
        for dep in graph[node]:
            walk(dep)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        walk(node)
    if not isinstance(data.get("seed", 21), int) or isinstance(data.get("seed", 21), bool):
        raise ValueError("Seed must be an integer")
    return data


def optimize(items, budget, capacity, factor):
    # Compare exact decimal assumptions; round only the presentation, never the incumbent.
    dec = lambda value: Decimal(str(value))
    budget, capacity, factor = dec(budget), dec(capacity), dec(factor)
    exact = [(x, dec(x["cost_k"]), dec(x["months"]), dec(x["benefit_k"]) * factor * dec(x["confidence"]) * (1 - dec(x["risk"]))) for x in items]
    best_net, best_cost = Decimal(0), Decimal(0)
    best = {"selected": [], "cost_k": 0, "months": 0, "adjusted_benefit_k": 0, "net_value_k": 0}
    for mask in range(1, 1 << len(items)):
        chosen = [x for i, x in enumerate(exact) if mask & (1 << i)]
        ids = {x[0]["id"] for x in chosen}
        if any(set(x[0]["depends_on"]) - ids for x in chosen):
            continue
        cost = sum(x[1] for x in chosen)
        months = sum(x[2] for x in chosen)
        if cost > budget or months > capacity:
            continue
        benefit = sum(x[3] for x in chosen)
        net = benefit - cost
        if net > best_net or (net > 0 and net == best_net and cost < best_cost):
            best_net, best_cost = net, cost
            best = {"selected": [x[0]["id"] for x in chosen], "cost_k": float(cost), "months": float(months),
                    "adjusted_benefit_k": float(round(benefit, 6)), "net_value_k": float(round(net, 6))}
    return best


def run(payload, context=None):
    data = validate(payload)
    items = data["initiatives"]
    selected = optimize(items, data["budget_k"], data["capacity_months"], data["benefit_factor"])
    selected_items = [x for x in items if x["id"] in selected["selected"]]
    frontier = []
    for multiplier in (0.5, 0.75, 1, 1.25):
        scenario_budget = float(Decimal(str(data["budget_k"])) * Decimal(str(multiplier)))
        frontier.append({"budget_k": scenario_budget, **optimize(items, scenario_budget, data["capacity_months"], data["benefit_factor"])})
    stress = [{"benefit_factor": factor, **optimize(items, data["budget_k"], data["capacity_months"], factor)} for factor in (0.5, 0.75, 1, 1.25)]
    rng = random.Random(data.get("seed", 21))
    simulations = sorted(sum(x["benefit_k"] * data["benefit_factor"] * x["confidence"] * (1-x["risk"]) * rng.triangular(0.5, 1.5, 1) for x in selected_items) - selected["cost_k"] for _ in range(500))
    waves, remaining, done = [], selected_items[:], set()
    while remaining:
        ready = [x for x in remaining if set(x["depends_on"]) <= done]
        waves.append([{"initiative": x["id"], "owner": x["owner"], "effort_months": x["months"]} for x in ready])
        done.update(x["id"] for x in ready)
        remaining = [x for x in remaining if x["id"] not in done]
    summary = (f"Fund {len(selected_items)} initiatives within the ${data['budget_k']:,.0f}k illustrative budget. "
               f"The selected set has ${selected['net_value_k']:,.1f}k in modeled risk-adjusted net value.") if selected_items else "Do not fund an initiative under these assumptions: no feasible set creates positive adjusted net value."
    model_brief = None
    if context is not None:
        model_brief = context.generate_json(task="Explain the computed portfolio selection for a director. Do not recalculate or invent financial facts. State the most important assumption and propose one validation milestone. Effort is in person-months, never elapsed duration or calendar months. Do not infer delivery dates.", data={"selection": {("effort_person_months" if k == "months" else k): v for k, v in selected.items()}, "stress": [{("effort_person_months" if k == "months" else k): v for k, v in row.items()} for row in stress], "owners": waves}, schema={"type": "object", "properties": {"brief": {"type": "string", "maxLength": 1200}, "assumption": {"type": "string", "maxLength": 500}, "validation_milestone": {"type": "string", "maxLength": 500}}, "required": ["brief", "assumption", "validation_milestone"], "additionalProperties": False})
    return {
        "summary": summary,
        "metrics": [{"label": "Selected initiatives", "value": len(selected_items), "unit": "of " + str(len(items))}, {"label": "Budget committed", "value": selected["cost_k"], "unit": "$k assumed"}, {"label": "Adjusted net value", "value": selected["net_value_k"], "unit": "$k modeled"}, {"label": "Capacity used", "value": selected["months"], "unit": "person-months"}],
        "evidence": ["Every feasible combination was evaluated; dependencies, budget and delivery capacity are hard constraints.", "Adjusted benefit = assumed annual benefit × benefit factor × confidence × (1 - risk). Net value subtracts one-time implementation cost; no discounting is applied.", "All financial inputs are fictional planning assumptions. Benefits are not observed savings or a valuation.", "Scenario spread uses 500 seeded triangular draws with independent benefits; it is an assumption sensitivity illustration, not a calibrated forecast."],
        "next_actions": ["Validate the highest-impact benefit assumption with the business owner before funding.", "Release funding against a measured baseline, an acceptance test and an accountable owner.", "Review dependency order and actual staffing before setting delivery dates."],
        "details": {"selection": selected, "selected_initiatives": selected_items, "deferred": [x["id"] for x in items if x["id"] not in selected["selected"]], "budget_frontier": frontier, "benefit_sensitivity": stress, "illustrative_net_value_spread_k": {"p10": round(simulations[49], 2), "p50": round(simulations[249], 2), "p90": round(simulations[449], 2)}, "dependency_waves": waves, "model_brief": model_brief, "mode": "structured model brief over computed optimization" if model_brief else "local exact optimization"},
    }


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
