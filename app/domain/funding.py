"""Revision-bound, sequential funding-evidence gates; no money is moved."""
from dataclasses import dataclass
from hashlib import sha256
import json
from decimal import Decimal
from app.domain.validation import number

STAGES=(("discovery",Decimal("0.10")),("pilot",Decimal("0.30")),("scale",Decimal("0.60")))

def assumption_revision(data):
    keys=("budget_k","capacity_months","benefit_factor","initiatives","discounted_cash_flow","benefit_overlaps")
    material={key:data[key] for key in keys if key in data}
    return sha256(json.dumps(material,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

@dataclass(frozen=True)
class FundingEvidence:
    initiative: str
    stage: str
    revision: str
    metric: str
    observed: float
    target: float
    operator: str
    source: str
    reviewer: str

    @property
    def criterion_passed(self):
        return self.observed>=self.target if self.operator==">=" else self.observed<=self.target

class FundingPolicy:
    def __init__(self,evidence):self.evidence=tuple(evidence)

    @classmethod
    def from_payload(cls,data):
        values=data.get("stage_evidence",[])
        if not isinstance(values,list) or len(values)>48:
            raise ValueError("Provide at most 48 stage-evidence records.")
        ids={item["id"] for item in data["initiatives"]};seen=set();rows=[]
        keys={"initiative","stage","assumption_revision","metric","observed","target","operator","source_reference","reviewer"}
        for value in values:
            if not isinstance(value,dict) or set(value)!=keys:
                raise ValueError("Stage evidence requires the documented initiative, stage, revision, criterion, source and reviewer fields.")
            if not isinstance(value["initiative"],str) or value["initiative"] not in ids or not isinstance(value["stage"],str) or value["stage"] not in dict(STAGES):
                raise ValueError("Stage evidence references an unknown initiative or funding stage.")
            key=(value["initiative"],value["stage"])
            if key in seen:raise ValueError("Duplicate evidence for an initiative/stage is not allowed.")
            seen.add(key)
            for field in ("metric","source_reference","reviewer"):
                if not isinstance(value[field],str) or not 1<=len(value[field].strip())<=300:
                    raise ValueError("Evidence metric, source and reviewer must be nonempty bounded text.")
            revision=value["assumption_revision"]
            if not isinstance(revision,str) or len(revision)!=64 or any(c not in "0123456789abcdef" for c in revision):
                raise ValueError("Evidence assumption_revision must be a lowercase SHA-256 digest.")
            if value["operator"] not in (">=","<="):raise ValueError("Evidence operator must be >= or <=.")
            observed=number(value["observed"],"observed",-1e12,1e12);target=number(value["target"],"target",-1e12,1e12)
            rows.append(FundingEvidence(value["initiative"],value["stage"],revision,value["metric"],observed,target,value["operator"],value["source_reference"],value["reviewer"]))
        return cls(rows)

    def evaluate(self,data,selection):
        revision=assumption_revision(data);lookup={(e.initiative,e.stage):e for e in self.evidence}
        items={item["id"]:item for item in data["initiatives"] if item["id"] in selection["selected"]}
        remaining=dict(items);ordered=[];done=set()
        while remaining:
            ready=[key for key,item in remaining.items() if set(item["depends_on"])<=done]
            for key in ready:ordered.append(remaining.pop(key));done.add(key)
        approved=set();rows=[];funding=[]
        for item in ordered:
            cumulative=Decimal(0);previous_passed=True
            for stage,fraction in STAGES:
                evidence=lookup.get((item["id"],stage));dependencies_ready=all((dep,stage) in approved for dep in item["depends_on"])
                status="evidence_missing"
                if evidence:
                    if evidence.revision!=revision:status="stale_revision"
                    elif not previous_passed:status="previous_stage_incomplete"
                    elif not dependencies_ready:status="dependency_stage_incomplete"
                    elif not evidence.criterion_passed:status="criterion_failed"
                    else:status="evidence_accepted"
                passed=status=="evidence_accepted"
                if passed:approved.add((item["id"],stage));cumulative+=fraction
                previous_passed=passed
                rows.append({"initiative":item["id"],"stage":stage,"status":status,"tranche_fraction":str(fraction),
                    "tranche_k":float(Decimal(str(item["cost_k"]))*fraction),
                    "metric":evidence.metric if evidence else None,"observed":evidence.observed if evidence else None,
                    "target":evidence.target if evidence else None,"operator":evidence.operator if evidence else None,
                    "reviewer":evidence.reviewer if evidence else None,"source_reference":evidence.source if evidence else None})
            funding.append({"initiative":item["id"],"eligible_fraction":str(cumulative),
                            "eligible_funding_k":float(Decimal(str(item["cost_k"]))*cumulative),"total_cost_k":item["cost_k"]})
        return {"assumption_revision":revision,"gates":rows,"funding":funding,
                "total_eligible_funding_k":float(sum((Decimal(str(row["eligible_funding_k"])) for row in funding),Decimal(0))),
                "scope":"Scenario evidence workflow only. Reviewer/source labels are supplied data, not authenticated approvals. No funding transaction is executed."}
