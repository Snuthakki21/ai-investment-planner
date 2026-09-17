"""Alternative discounted selection, overlap diagnostics and correlated regret."""
from dataclasses import dataclass
from decimal import Decimal
import math
import random
from app.domain.optimization import FeasibleSet, ZERO, decimal
from app.domain.valuation import DiscountAssumptions, OverlapPolicy
from app.domain.funding import FundingPolicy
from app.domain.validation import number

@dataclass(frozen=True)
class SensitivityAssumptions:
    paths: int = 100
    correlation: float = .60
    spread: float = .30

    @classmethod
    def from_payload(cls,data):
        values=data.get("correlated_sensitivity",{})
        if not isinstance(values,dict) or set(values)-{"paths","correlation","spread"}:
            raise ValueError("Unknown correlated-sensitivity option.")
        paths=values.get("paths",100)
        if type(paths) is not int or not 20<=paths<=500:
            raise ValueError("Sensitivity paths must be an integer from 20 to 500.")
        correlation=number(values.get("correlation",.6),"correlation",0,1)
        spread=number(values.get("spread",.3),"spread",0,1)
        return cls(paths,float(correlation),float(spread))

class InvestmentAnalysis:
    def __init__(self,discount,overlaps,funding,sensitivity):
        self.discount=discount;self.overlaps=overlaps;self.funding=funding;self.sensitivity=sensitivity

    @classmethod
    def from_payload(cls,data):
        return cls(DiscountAssumptions.from_payload(data),OverlapPolicy.from_payload(data),
                   FundingPolicy.from_payload(data),SensitivityAssumptions.from_payload(data))

    def analyze(self,data,legacy_selection):
        space=FeasibleSet(data["initiatives"],data["budget_k"],data["capacity_months"])
        base={item.identity:item.adjusted_benefit(decimal(data["benefit_factor"])) for item in space.initiatives}
        benefit_factor=sum(((1+self.discount.growth)**(year-1)/(1+self.discount.rate)**year for year in range(1,self.discount.years+1)),ZERO)
        cost_factor=1+self.discount.operating_cost_fraction*sum((1/(1+self.discount.rate)**year for year in range(1,self.discount.years+1)),ZERO)
        def evaluate(portfolio,benefits=base):
            adjusted,_=self.overlaps.adjust({name:benefits[name] for name in portfolio.identifiers})
            return adjusted*benefit_factor-portfolio.cost*cost_factor
        selected,npv=space.choose(evaluate)
        adjusted,deductions=self.overlaps.adjust({name:base[name] for name in selected.identifiers})
        legacy=next(portfolio for portfolio in space.portfolios if set(portfolio.identifiers)==set(legacy_selection["selected"]))
        ranking=sorted(space.portfolios,key=lambda p:(-evaluate(p),p.cost,p.identifiers))
        candidates=[]
        for candidate in [selected,legacy,space.portfolios[0],*ranking[:8]]:
            if candidate.identifiers not in {c.identifiers for c in candidates}:candidates.append(candidate)
        rng=random.Random(data.get("seed",21));totals={p.identifiers:[] for p in candidates};regrets={p.identifiers:[] for p in candidates};wins={p.identifiers:0 for p in candidates}
        for _ in range(self.sensitivity.paths):
            common=rng.gauss(0,1);shocked={}
            for name,value in base.items():
                latent=math.sqrt(self.sensitivity.correlation)*common+math.sqrt(1-self.sensitivity.correlation)*rng.gauss(0,1)
                factor=max(0,min(3,1+self.sensitivity.spread*latent))
                shocked[name]=value*Decimal(str(round(factor,8)))
            values={p.identifiers:evaluate(p,shocked) for p in candidates};best=max(values.values())
            for key,value in values.items():
                totals[key].append(value);regrets[key].append(best-value)
                if value==best:wins[key]+=1
        rows=[]
        for portfolio in candidates:
            outcomes=sorted(totals[portfolio.identifiers]);regret=regrets[portfolio.identifiers]
            rows.append({"selected":list(portfolio.identifiers),"assumed_npv_k":float(round(evaluate(portfolio),6)),
                         "mean_scenario_npv_k":float(round(sum(outcomes,ZERO)/len(outcomes),6)),
                         "p10_npv_k":float(round(outcomes[math.ceil(.1*len(outcomes))-1],6)),
                         "p90_npv_k":float(round(outcomes[math.ceil(.9*len(outcomes))-1],6)),
                         "mean_regret_k":float(round(sum(regret,ZERO)/len(regret),6)),
                         "best_in_path_count":wins[portfolio.identifiers]})
        return {"discounted_analysis":{"selection":{"selected":list(selected.identifiers),"cost_k":float(selected.cost),
                    "effort_person_months":float(selected.effort),"npv_k":float(round(npv,6)),"adjusted_annual_benefit_k":float(round(adjusted,6))},
                    "legacy_selection_npv_k":float(round(evaluate(legacy),6)),"assumptions":{"horizon_years":self.discount.years,
                        "discount_rate":str(self.discount.rate),"annual_benefit_growth":str(self.discount.growth),
                        "annual_operating_cost_fraction":str(self.discount.operating_cost_fraction)},
                    "cash_flows":self.discount.cash_flows(adjusted,selected.cost),"time_zero_cost_k":float(selected.cost),
                    "overlap_deductions":deductions,"feasible_portfolios":len(space.portfolios),
                    "objective":"Separate discounted objective: year-end adjusted benefits minus annual operating cost, discounted to time zero, less initial implementation cost. The legacy one-year adjusted net-value result is preserved."},
                "funding_evidence":self.funding.evaluate(data,legacy_selection),
                "correlated_sensitivity":{"paths":self.sensitivity.paths,"seed":data.get("seed",21),
                    "latent_correlation":self.sensitivity.correlation,"spread":self.sensitivity.spread,"candidate_policies":rows,
                    "candidate_selection":"Legacy choice, discounted choice, no funding, and top eight feasible sets under base NPV, deduplicated.",
                    "interpretation":"Seeded synthetic common-factor benefit sensitivity. Expected regret is relative only to the displayed candidate policies under assumed draws, not a calibrated forecast or global hindsight optimum. Ties count as best for every tied policy."}}
