"""Typed initiative values and exact dependency/budget constrained enumeration."""
from dataclasses import dataclass
from decimal import Decimal

ZERO=Decimal(0)
def decimal(value):return Decimal(str(value))

@dataclass(frozen=True)
class Initiative:
    identity: str
    cost: Decimal
    effort: Decimal
    benefit: Decimal
    confidence: Decimal
    risk: Decimal
    dependencies: frozenset

    @classmethod
    def from_mapping(cls,item):
        return cls(item["id"],decimal(item["cost_k"]),decimal(item["months"]),decimal(item["benefit_k"]),
                   decimal(item["confidence"]),decimal(item["risk"]),frozenset(item["depends_on"]))

    def adjusted_benefit(self,factor):
        return self.benefit*factor*self.confidence*(1-self.risk)

@dataclass(frozen=True)
class FeasiblePortfolio:
    indices: tuple
    identifiers: tuple
    cost: Decimal
    effort: Decimal

class FeasibleSet:
    """Enumerate once; share feasible candidates across alternative objective analyses."""
    def __init__(self,items,budget,capacity):
        self.initiatives=tuple(Initiative.from_mapping(item) for item in items)
        self.budget=decimal(budget);self.capacity=decimal(capacity)
        portfolios=[FeasiblePortfolio((),(),ZERO,ZERO)]
        for mask in range(1,1<<len(self.initiatives)):
            indices=tuple(i for i in range(len(self.initiatives)) if mask&(1<<i))
            chosen=[self.initiatives[i] for i in indices]
            ids=frozenset(item.identity for item in chosen)
            if any(item.dependencies-ids for item in chosen):continue
            cost=sum((item.cost for item in chosen),ZERO)
            effort=sum((item.effort for item in chosen),ZERO)
            if cost<=self.budget and effort<=self.capacity:
                portfolios.append(FeasiblePortfolio(indices,tuple(item.identity for item in chosen),cost,effort))
        self.portfolios=tuple(portfolios)

    def choose(self,objective):
        best=self.portfolios[0];best_value=ZERO
        for candidate in self.portfolios[1:]:
            value=objective(candidate)
            if value>best_value or (value>ZERO and value==best_value and candidate.cost<best.cost):
                best,best_value=candidate,value
        return best,best_value

class ExactOptimizer:
    def select(self,items,budget,capacity,factor):
        space=FeasibleSet(items,budget,capacity)
        benefits=[item.adjusted_benefit(decimal(factor)) for item in space.initiatives]
        chosen,value=space.choose(lambda portfolio:sum((benefits[i] for i in portfolio.indices),ZERO)-portfolio.cost)
        gross=sum((benefits[i] for i in chosen.indices),ZERO)
        return {"selected":list(chosen.identifiers),"cost_k":float(chosen.cost),"months":float(chosen.effort),
                "adjusted_benefit_k":float(round(gross,6)),"net_value_k":float(round(value,6))}

optimize=ExactOptimizer().select
