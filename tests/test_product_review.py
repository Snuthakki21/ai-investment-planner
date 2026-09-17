"""Independent Staff review: objective oracle, evidence sequence and immutable assumptions."""
from copy import deepcopy
from decimal import Decimal
from itertools import combinations
import unittest
from app.domain.funding import assumption_revision
from projects.ai_investment_planner.project import default_input, run

class IndependentProductReview(unittest.TestCase):
    def small(self):
        p=default_input();p.update(budget_k=100,capacity_months=10,benefit_factor=1,initiatives=[dict(id='foundation',name='Foundation',owner='platform',cost_k=20,months=2,benefit_k=20,confidence=1,risk=0,depends_on=[]),dict(id='assistant',name='Assistant',owner='operations',cost_k=50,months=4,benefit_k=80,confidence=1,risk=0,depends_on=['foundation']),dict(id='classifier',name='Classifier',owner='risk',cost_k=40,months=3,benefit_k=50,confidence=1,risk=0,depends_on=[])])
        p['discounted_cash_flow']={'horizon_years':2,'discount_rate':.1,'annual_operating_cost_fraction':.1}
        p['correlated_sensitivity']={'paths':20,'spread':0}
        return p

    def test_discounted_choice_matches_independent_small_universe(self):
        p=self.small();candidates=[]
        for count in range(4):
            for choice in combinations(p['initiatives'],count):
                ids={x['id'] for x in choice};cost=sum(x['cost_k'] for x in choice)
                if cost>100 or sum(x['months'] for x in choice)>10 or any(set(x['depends_on'])-ids for x in choice):continue
                benefit=sum(x['benefit_k'] for x in choice); cash=Decimal(benefit)-Decimal(cost)/10
                npv=cash/Decimal('1.1')+cash/Decimal('1.21')-cost
                candidates.append((npv,ids))
        expected=max(candidates,key=lambda row:row[0]);actual=run(p)['details']['discounted_analysis']['selection']
        self.assertEqual(set(actual['selected']),expected[1]);self.assertAlmostEqual(actual['npv_k'],float(expected[0]),places=5)

    def test_missing_foundation_blocks_dependent_funding_even_if_input_order_reversed(self):
        p=self.small();p['initiatives'].reverse();revision=assumption_revision(p)
        p['stage_evidence']=[dict(initiative='assistant',stage='discovery',assumption_revision=revision,metric='acceptance',observed=1,target=1,operator='>=',source_reference='synthetic evidence',reviewer='reviewer')]
        d=run(p)['details']['funding_evidence'];row=next(r for r in d['gates'] if r['initiative']=='assistant' and r['stage']=='discovery')
        self.assertEqual(row['status'],'dependency_stage_incomplete');self.assertEqual(d['total_eligible_funding_k'],0)

    def test_changed_overlap_assumptions_invalidate_prior_evidence(self):
        p=self.small();revision=assumption_revision(p)
        p['stage_evidence']=[dict(initiative='foundation',stage='discovery',assumption_revision=revision,metric='acceptance',observed=1,target=1,operator='>=',source_reference='synthetic evidence',reviewer='reviewer')]
        p['benefit_overlaps']=[dict(name='overlap',members=['assistant','classifier'],overlap_fraction=.2)]
        d=run(p)['details']['funding_evidence'];self.assertEqual(d['gates'][0]['status'],'stale_revision')

    def test_no_funding_policy_is_visible_under_unprofitable_assumptions(self):
        p=self.small();p['benefit_factor']=0;d=run(p)['details']
        self.assertEqual(d['selection']['selected'],[]);self.assertEqual(d['discounted_analysis']['selection']['selected'],[])
        self.assertEqual(d['funding_evidence']['total_eligible_funding_k'],0)
        self.assertTrue(any(row['selected']==[] for row in d['correlated_sensitivity']['candidate_policies']))

    def test_analysis_leaves_input_and_nested_evidence_unchanged(self):
        p=self.small();before=deepcopy(p);run(p);self.assertEqual(p,before)
