"""Declared independent-benefit sensitivity and dependency delivery ordering."""
import random

class PlanningSensitivity:
    def analyze(self, data, selected, selected_items):
        rng = random.Random(data.get("seed", 21))
        simulations = sorted(sum(x["benefit_k"] * data["benefit_factor"] * x["confidence"] * (1-x["risk"]) * rng.triangular(0.5, 1.5, 1) for x in selected_items) - selected["cost_k"] for _ in range(500))
        waves, remaining, done = [], selected_items[:], set()
        while remaining:
            ready = [x for x in remaining if set(x["depends_on"]) <= done]
            waves.append([{"initiative": x["id"], "owner": x["owner"], "effort_months": x["months"]} for x in ready])
            done.update(x["id"] for x in ready)
            remaining = [x for x in remaining if x["id"] not in done]
        return simulations, waves
