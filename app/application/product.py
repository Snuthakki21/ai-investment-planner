"""Exact investment selection, discounted alternatives and funding evidence."""
from decimal import Decimal
from app.domain.validation import validate
from app.domain.optimization import optimize
from app.domain.sensitivity import PlanningSensitivity
from app.domain.analysis import InvestmentAnalysis
from app.ai.brief import InvestmentBrief

class ProductApplication:
    def run(self, payload, context=None):
        data = validate(payload)
        analysis = InvestmentAnalysis.from_payload(data)
        items = data["initiatives"]
        selected = optimize(items, data["budget_k"], data["capacity_months"], data["benefit_factor"])
        selected_items = [x for x in items if x["id"] in selected["selected"]]
        frontier = []
        for multiplier in (0.5, 0.75, 1, 1.25):
            scenario_budget = float(Decimal(str(data["budget_k"])) * Decimal(str(multiplier)))
            frontier.append({"budget_k": scenario_budget, **optimize(items, scenario_budget, data["capacity_months"], data["benefit_factor"])})
        stress = [{"benefit_factor": factor, **optimize(items, data["budget_k"], data["capacity_months"], factor)} for factor in (0.5, 0.75, 1, 1.25)]
        simulations, waves = PlanningSensitivity().analyze(data, selected, selected_items)
        summary = (f"Fund {len(selected_items)} initiatives within the ${data['budget_k']:,.0f}k illustrative budget. "
                   f"The selected set has ${selected['net_value_k']:,.1f}k in modeled risk-adjusted net value.") if selected_items else "Do not fund an initiative under these assumptions: no feasible set creates positive adjusted net value."
        model_brief = InvestmentBrief().generate(selected, stress, waves, context)
        report = {
            "summary": summary,
            "metrics": [{"label": "Selected initiatives", "value": len(selected_items), "unit": "of " + str(len(items))}, {"label": "Budget committed", "value": selected["cost_k"], "unit": "$k assumed"}, {"label": "Adjusted net value", "value": selected["net_value_k"], "unit": "$k modeled"}, {"label": "Capacity used", "value": selected["months"], "unit": "person-months"}],
            "evidence": ["Every feasible combination was evaluated; dependencies, budget and delivery capacity are hard constraints.", "Adjusted benefit = assumed annual benefit × benefit factor × confidence × (1 - risk). Net value subtracts one-time implementation cost; no discounting is applied.", "All financial inputs are fictional planning assumptions. Benefits are not observed savings or a valuation.", "Scenario spread uses 500 seeded triangular draws with independent benefits; it is an assumption sensitivity illustration, not a calibrated forecast."],
            "next_actions": ["Validate the highest-impact benefit assumption with the business owner before funding.", "Release funding against a measured baseline, an acceptance test and an accountable owner.", "Review dependency order and actual staffing before setting delivery dates."],
            "details": {"selection": selected, "selected_initiatives": selected_items, "deferred": [x["id"] for x in items if x["id"] not in selected["selected"]], "budget_frontier": frontier, "benefit_sensitivity": stress, "illustrative_net_value_spread_k": {"p10": round(simulations[49], 2), "p50": round(simulations[249], 2), "p90": round(simulations[449], 2)}, "dependency_waves": waves, "model_brief": model_brief, "mode": "structured model brief over computed optimization" if model_brief else "local exact optimization"},
        }
        report["details"].update(analysis.analyze(data, selected))
        return report
