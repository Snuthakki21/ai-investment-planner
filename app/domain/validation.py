"""Investment assumption validation and dependency-cycle detection."""
import copy
import math
def number(value, field, low=0, high=1e7):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high or (isinstance(value, float) and not math.isfinite(value)):
        raise ValueError(f"{field} must be finite and between {low} and {high}")
    return value
def validate(payload):
    if not isinstance(payload, dict):
        raise ValueError("Input must be an object")
    data = copy.deepcopy(payload)
    for name in ("budget_k", "capacity_months", "benefit_factor"):
        number(data.get(name), name, 0, 100000 if name != "benefit_factor" else 3)
    initiatives = data.get("initiatives")
    if not isinstance(initiatives, list) or not 1 <= len(initiatives) <= 16:
        raise ValueError("Provide 1 to 16 initiatives for exact bounded optimization")
    ids = set()
    for item in initiatives:
        if not isinstance(item, dict):
            raise ValueError("Every initiative must be an object")
        for field in ("id", "name", "owner"):
            if not isinstance(item.get(field), str) or not 1 <= len(item[field]) <= 100:
                raise ValueError(f"Each initiative needs a short {field}")
        if item["id"] in ids:
            raise ValueError("Initiative identifiers must be unique")
        ids.add(item["id"])
        for field in ("cost_k", "months", "benefit_k"):
            number(item.get(field), field, 0, 100000)
        for field in ("confidence", "risk"):
            number(item.get(field), field, 0, 1)
        if not isinstance(item.get("depends_on"), list) or not all(isinstance(x, str) for x in item["depends_on"]):
            raise ValueError("Dependencies must be a list of identifiers")
    graph = {item["id"]: set(item["depends_on"]) for item in initiatives}
    if any(deps - ids for deps in graph.values()):
        raise ValueError("Unknown dependency")
    visited, visiting = set(), set()
    def walk(node):
        if node in visiting:
            raise ValueError("Dependency cycle detected")
        if node in visited:
            return
        visiting.add(node)
        for dep in graph[node]:
            walk(dep)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        walk(node)
    if not isinstance(data.get("seed", 21), int) or isinstance(data.get("seed", 21), bool):
        raise ValueError("Seed must be an integer")
    return data
