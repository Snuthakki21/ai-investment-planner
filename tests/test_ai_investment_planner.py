import copy
import unittest
from portfolio.registry import projects
p = projects()["ai_investment_planner"]

class InvestmentTests(unittest.TestCase):
    def test_selection_satisfies_constraints(self):
        data = p.default_input()
        r = p.run(data)["details"]["selection"]
        self.assertLessEqual(r["cost_k"], data["budget_k"])
        self.assertLessEqual(r["months"], data["capacity_months"])
        selected = set(r["selected"])
        for item in data["initiatives"]:
            if item["id"] in selected:
                self.assertTrue(set(item["depends_on"]) <= selected)

    def test_known_optimum(self):
        d = p.default_input()
        d["initiatives"] = [dict(x, depends_on=[], confidence=1, risk=0, months=1) for x in d["initiatives"][:2]]
        d["budget_k"] = 110
        self.assertEqual(p.run(d)["details"]["selection"]["selected"], ["test-data"])

    def test_no_value_no_funding(self):
        d = p.default_input(); d["benefit_factor"] = 0
        self.assertEqual(p.run(d)["details"]["selection"]["selected"], [])

    def test_cycle_rejected(self):
        d = p.default_input(); d["initiatives"][0]["depends_on"] = ["test-data"]
        with self.assertRaises(ValueError): p.run(d)

    def test_unknown_dependency(self):
        d = p.default_input(); d["initiatives"][0]["depends_on"] = ["missing"]
        with self.assertRaises(ValueError): p.run(d)

    def test_nonfinite_rejected(self):
        d = p.default_input(); d["budget_k"] = float("nan")
        with self.assertRaises(ValueError): p.run(d)

    def test_budget_changes_selection(self):
        d = p.default_input(); first = p.run(d)["details"]["selection"]["selected"]
        d["budget_k"] = 150
        self.assertNotEqual(first, p.run(d)["details"]["selection"]["selected"])

    def test_seed_reproducibility(self):
        self.assertEqual(p.run(p.default_input()), p.run(p.default_input()))
