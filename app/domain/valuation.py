"""Discounted cash flow and explicit benefit-overlap policies."""
from dataclasses import dataclass
from decimal import Decimal
from app.domain.optimization import ZERO, decimal
from app.domain.validation import number

@dataclass(frozen=True)
class DiscountAssumptions:
    years: int = 3
    rate: Decimal = Decimal("0.10")
    growth: Decimal = ZERO
    operating_cost_fraction: Decimal = Decimal("0.08")

    @classmethod
    def from_payload(cls,payload):
        values=payload.get("discounted_cash_flow",{})
        if not isinstance(values,dict) or set(values)-{"horizon_years","discount_rate","annual_benefit_growth","annual_operating_cost_fraction"}:
            raise ValueError("Unknown discounted cash-flow option.")
        years=values.get("horizon_years",3)
        if type(years) is not int or not 1<=years<=10:
            raise ValueError("DCF horizon must be an integer from one to ten years.")
        rate=number(values.get("discount_rate",.1),"discount_rate",0,1)
        growth=number(values.get("annual_benefit_growth",0),"annual_benefit_growth",-.5,.5)
        operating=number(values.get("annual_operating_cost_fraction",.08),"annual_operating_cost_fraction",0,1)
        return cls(years,decimal(rate),decimal(growth),decimal(operating))

    def cash_flows(self,benefit,cost):
        rows=[]
        for year in range(1,self.years+1):
            gross=benefit*(1+self.growth)**(year-1)
            operating=cost*self.operating_cost_fraction
            cash=gross-operating
            discounted=cash/(1+self.rate)**year
            rows.append({"year":year,"gross_benefit_k":float(round(gross,6)),"operating_cost_k":float(round(operating,6)),
                         "net_cash_flow_k":float(round(cash,6)),"discounted_cash_flow_k":float(round(discounted,6))})
        return rows

    def value(self,benefit,cost):
        # Preserve Decimal precision for comparisons; round only report fields.
        return sum(((benefit*(1+self.growth)**(year-1)-cost*self.operating_cost_fraction)/(1+self.rate)**year
                    for year in range(1,self.years+1)),ZERO)-cost

@dataclass(frozen=True)
class BenefitOverlap:
    name: str
    members: frozenset
    fraction: Decimal

class OverlapPolicy:
    def __init__(self,groups):self.groups=tuple(groups)

    @classmethod
    def from_payload(cls,payload):
        values=payload.get("benefit_overlaps",[])
        if not isinstance(values,list) or len(values)>16:
            raise ValueError("Provide at most sixteen benefit-overlap groups.")
        ids={item["id"] for item in payload["initiatives"]};used=set();names=set();groups=[]
        for value in values:
            if not isinstance(value,dict) or set(value)!={"name","members","overlap_fraction"}:
                raise ValueError("Each overlap group needs name, members and overlap_fraction.")
            name=value["name"];members=value["members"]
            if not isinstance(name,str) or not 1<=len(name)<=100 or name in names:
                raise ValueError("Overlap group names must be unique short strings.")
            if not isinstance(members,list) or len(members)<2 or any(not isinstance(x,str) for x in members) or len(set(members))!=len(members) or set(members)-ids:
                raise ValueError("Overlap groups need at least two unique known initiative identifiers.")
            if used & set(members):raise ValueError("An initiative cannot belong to multiple overlap groups.")
            fraction=decimal(number(value["overlap_fraction"],"overlap_fraction",0,1))
            groups.append(BenefitOverlap(name,frozenset(members),fraction));used.update(members);names.add(name)
        return cls(groups)

    def adjust(self,benefits):
        total=sum(benefits.values(),ZERO);deductions=[]
        for group in self.groups:
            selected=[value for name,value in benefits.items() if name in group.members]
            deduction=group.fraction*(sum(selected,ZERO)-max(selected)) if len(selected)>1 else ZERO
            total-=deduction
            deductions.append({"group":group.name,"selected_members":sorted(group.members & benefits.keys()),
                               "overlap_fraction":str(group.fraction),"annual_benefit_deduction_k":float(round(deduction,6))})
        return total,deductions
