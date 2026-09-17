"""Exact objectives, benefit overlap, staged evidence and correlated sensitivity."""
from copy import deepcopy
from decimal import Decimal
import unittest
from app.application.product import ProductApplication
from app.domain.optimization import ExactOptimizer, FeasibleSet, Initiative
from app.domain.valuation import DiscountAssumptions, OverlapPolicy
from app.domain.funding import FundingPolicy, assumption_revision
from projects.ai_investment_planner.project import default_input,run


def evidence(data,initiative,stage,**changes):
    return dict(initiative=initiative,stage=stage,assumption_revision=assumption_revision(data),
                metric="verified acceptance rate",observed=95,target=90,operator=">=",
                source_reference="synthetic evaluation record",reviewer="Committee reviewer",**changes)

class InvestmentProductTests(unittest.TestCase):
    def test_application_compatibility(self):
        self.assertEqual(ProductApplication().run(default_input()),run(default_input()))

    def test_npv_matches_independent_discount_formula(self):
        p=default_input();p["initiatives"]=[dict(p["initiatives"][0],cost_k=100,benefit_k=200,confidence=1,risk=0)]
        p["discounted_cash_flow"]={"horizon_years":2,"discount_rate":.1,"annual_benefit_growth":.05,"annual_operating_cost_fraction":.1}
        result=run(p)["details"]["discounted_analysis"]
        expected=Decimal(190)/Decimal("1.1")+Decimal(200)/Decimal("1.21")-100
        self.assertAlmostEqual(result["selection"]["npv_k"],float(expected),places=5)
        self.assertEqual(result["cash_flows"][1]["gross_benefit_k"],210)
        self.assertAlmostEqual(DiscountAssumptions.from_payload(p).value(Decimal(200),Decimal(100)),expected)

    def test_legacy_selection_is_unchanged_by_dcf_assumptions(self):
        p=default_input();before=run(p)["details"]["selection"]
        p["discounted_cash_flow"]={"horizon_years":10,"discount_rate":.5}
        self.assertEqual(run(p)["details"]["selection"],before)

    def test_overlap_deduplicates_only_smaller_shared_benefit(self):
        p=default_input();p["benefit_overlaps"]=[{"name":"shared support time","members":["incident","policy"],"overlap_fraction":1}]
        overlap=OverlapPolicy.from_payload(p)
        adjusted,rows=overlap.adjust({"incident":Decimal(100),"policy":Decimal(80)})
        self.assertEqual(adjusted,Decimal(100))
        self.assertEqual(rows[0]["annual_benefit_deduction_k"],80)
        self.assertEqual(overlap.adjust({"incident":Decimal(100)})[0],Decimal(100))

    def test_discounted_choice_cannot_exceed_budget_or_capacity(self):
        p=default_input();d=run(p)["details"]["discounted_analysis"]["selection"]
        self.assertLessEqual(d["cost_k"],p["budget_k"])
        self.assertLessEqual(d["effort_person_months"],p["capacity_months"])
        for item in p["initiatives"]:
            if item["id"] in d["selected"]:self.assertTrue(set(item["depends_on"])<=set(d["selected"]))

    def test_evidence_is_bound_to_current_assumptions(self):
        p=default_input();p["stage_evidence"]=[evidence(p,"data-foundation","discovery")]
        accepted=run(p)["details"]["funding_evidence"]
        row=next(row for row in accepted["gates"] if row["initiative"]=="data-foundation" and row["stage"]=="discovery")
        self.assertEqual(row["status"],"evidence_accepted")
        p["budget_k"]+=1
        stale=run(p)["details"]["funding_evidence"]
        row=next(row for row in stale["gates"] if row["initiative"]=="data-foundation" and row["stage"]=="discovery")
        self.assertEqual(row["status"],"stale_revision")
        self.assertEqual(stale["total_eligible_funding_k"],0)

    def test_funding_stages_cannot_be_skipped(self):
        p=default_input();p["stage_evidence"]=[evidence(p,"data-foundation","pilot")]
        d=run(p)["details"]["funding_evidence"]
        row=next(row for row in d["gates"] if row["initiative"]=="data-foundation" and row["stage"]=="pilot")
        self.assertEqual(row["status"],"previous_stage_incomplete")
        self.assertEqual(d["total_eligible_funding_k"],0)

    def test_dependency_stage_must_be_ready(self):
        p=default_input();p["stage_evidence"]=[evidence(p,"test-data","discovery")]
        d=run(p)["details"]["funding_evidence"]
        row=next(row for row in d["gates"] if row["initiative"]=="test-data" and row["stage"]=="discovery")
        self.assertEqual(row["status"],"dependency_stage_incomplete")

    def test_failed_threshold_rejects_gate(self):
        p=default_input();record=evidence(p,"data-foundation","discovery");record["observed"]=89;p["stage_evidence"]=[record]
        d=run(p)["details"]["funding_evidence"]
        self.assertEqual(d["gates"][0]["status"],"criterion_failed")

    def test_all_stages_release_full_modelled_cost(self):
        p=default_input();selection=run(p)["details"]["selection"]
        p["stage_evidence"]=[evidence(p,name,stage) for name in selection["selected"] for stage in ("discovery","pilot","scale")]
        d=run(p)["details"]["funding_evidence"]
        self.assertTrue(all(row["status"]=="evidence_accepted" for row in d["gates"]))
        self.assertEqual(d["total_eligible_funding_k"],selection["cost_k"])

    def test_lower_is_better_criterion(self):
        p=default_input();record=evidence(p,"data-foundation","discovery");record.update(observed=10,target=20,operator="<=")
        p["stage_evidence"]=[record]
        self.assertEqual(run(p)["details"]["funding_evidence"]["gates"][0]["status"],"evidence_accepted")

    def test_revision_excludes_own_evidence_and_sensitivity_seed(self):
        p=default_input();before=assumption_revision(p);p["stage_evidence"]=[evidence(p,"data-foundation","discovery")];p["seed"]=444
        self.assertEqual(assumption_revision(p),before)

    def test_seeded_regret_is_reproducible_and_nonnegative(self):
        p=default_input();a=run(p)["details"]["correlated_sensitivity"];b=run(p)["details"]["correlated_sensitivity"]
        self.assertEqual(a,b)
        self.assertTrue(all(row["mean_regret_k"]>=0 for row in a["candidate_policies"]))
        p["seed"]=333
        self.assertNotEqual(a["candidate_policies"],run(p)["details"]["correlated_sensitivity"]["candidate_policies"])

    def test_zero_spread_has_zero_regret_for_discounted_optimum(self):
        p=default_input();p["correlated_sensitivity"]={"spread":0,"paths":20}
        rows=run(p)["details"]["correlated_sensitivity"]["candidate_policies"]
        self.assertEqual(rows[0]["mean_regret_k"],0)
        self.assertEqual(rows[0]["best_in_path_count"],20)

    def test_invalid_new_assumptions_fail_before_provider_call(self):
        class Context:
            def generate_json(self,**kwargs):raise AssertionError("Invalid payload reached provider")
        mutations=[("discounted_cash_flow",[]),("discounted_cash_flow",{"horizon_years":0}),("discounted_cash_flow",{"discount_rate":float("nan")}),
                   ("discounted_cash_flow",{"unknown":1}),("correlated_sensitivity",{"paths":True}),("correlated_sensitivity",{"paths":501}),
                   ("correlated_sensitivity",{"correlation":1.1}),("correlated_sensitivity",{"unknown":1}),("stage_evidence",[])]
        for key,value in mutations[:-1]:
            p=default_input();p[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):run(p,Context())

    def test_malformed_or_duplicate_stage_evidence_is_rejected(self):
        p=default_input();good=evidence(p,"data-foundation","discovery")
        variants=[None,{},dict(good,initiative="missing"),dict(good,stage=[]),dict(good,metric=""),dict(good,assumption_revision="bad"),dict(good,operator="="),dict(good,observed=True)]
        for record in variants:
            p=default_input();p["stage_evidence"]=[record]
            with self.subTest(record=record),self.assertRaises(ValueError):run(p)
        p["stage_evidence"]=[good,good]
        with self.assertRaises(ValueError):run(p)

    def test_overlapping_membership_and_unknown_overlap_are_rejected(self):
        good={"name":"first","members":["incident","policy"],"overlap_fraction":.5}
        for groups in [None,[{}],[dict(good,name="")],[dict(good,members=["missing","policy"])],[dict(good,members=["policy","policy"])],[good,dict(good,name="second")]]:
            p=default_input();p["benefit_overlaps"]=groups
            with self.subTest(groups=groups),self.assertRaises(ValueError):run(p)

if __name__=="__main__":unittest.main()
