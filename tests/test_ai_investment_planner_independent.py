"""Independent reviewer reproductions for investment optimizer findings."""
import unittest
from projects.ai_investment_planner.project import default_input,run

def initiative(identity,cost,benefit):
    return dict(id=identity,name=identity,owner='Demo',cost_k=cost,months=1,benefit_k=benefit,confidence=1,risk=0,depends_on=[])

class IndependentInvestmentReview(unittest.TestCase):
    def test_incumbent_rounding_does_not_choose_worse_set(self):
        p=default_input();p.update(budget_k=1,capacity_months=1,benefit_factor=1,initiatives=[initiative('better',1,1.1004),initiative('worse',1,1.1003)])
        self.assertEqual(run(p)['details']['selection']['selected'],['better'])

    def test_exact_budget_boundary_remains_feasible(self):
        p=default_input();p.update(budget_k=0.3,capacity_months=2,benefit_factor=1,initiatives=[initiative('first',0.1,1),initiative('second',0.2,1)])
        self.assertEqual(run(p)['details']['selection']['selected'],['first','second'])

    def test_root_input_contract(self):
        for bad in [None,[], 'not an object']:
            with self.subTest(bad=bad),self.assertRaises(ValueError):run(bad)

    def test_decimal_assumptions_can_resolve_small_improvement(self):
        p=default_input();p.update(budget_k=1,capacity_months=1,benefit_factor=1,initiatives=[initiative('earlier',1,1.1006),initiative('better',1,1.1009)])
        self.assertEqual(run(p)['details']['selection']['selected'],['better'])

    def test_invalid_initiative_shapes_are_controlled(self):
        mutations=[lambda p:p.update(initiatives=[]),lambda p:p.update(initiatives=[None]),lambda p:p['initiatives'][0].update(name=''),lambda p:p['initiatives'].append(dict(p['initiatives'][0])),lambda p:p['initiatives'][0].update(depends_on=None),lambda p:p.update(seed=True)]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                p=default_input();mutation(p)
                with self.assertRaises(ValueError):run(p)

    def test_model_brief_preserves_selection_and_person_month_units(self):
        class Context:
            def generate_json(self,**kwargs):
                self.request=kwargs
                return dict(brief='Draft for review',assumption='Benefits are assumed',validation_milestone='Measure baseline')
        context=Context();p=default_input();baseline=run(p);result=run(p,context)
        self.assertEqual(result['details']['selection'],baseline['details']['selection'])
        self.assertEqual(result['details']['model_brief']['brief'],'Draft for review')
        self.assertIn('person-months',context.request['task'])
        self.assertIn('effort_person_months',context.request['data']['selection'])
        self.assertNotIn('months',context.request['data']['selection'])
        self.assertTrue(all('effort_person_months' in item and 'months' not in item for item in context.request['data']['stress']))

    def test_frontier_reports_the_same_budget_used_for_feasibility(self):
        p=default_input();p.update(budget_k=.3,capacity_months=1,benefit_factor=1,initiatives=[initiative('just_above',.377,1)])
        row=run(p)['details']['budget_frontier'][-1]
        self.assertEqual(row['budget_k'],.375)
        self.assertEqual(row['selected'],[])
        p['initiatives'][0]['cost_k']=.374
        self.assertEqual(run(p)['details']['budget_frontier'][-1]['selected'],['just_above'])
