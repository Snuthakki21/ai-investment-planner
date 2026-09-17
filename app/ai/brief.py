"""Optional model narrative receives calculated facts and person-month effort."""
class InvestmentBrief:
    def generate(self, selected, stress, waves, context=None):
        model_brief = None
        if context is not None:
            model_brief = context.generate_json(task="Explain the computed portfolio selection for a director. Do not recalculate or invent financial facts. State the most important assumption and propose one validation milestone. Effort is in person-months, never elapsed duration or calendar months. Do not infer delivery dates.", data={"selection": {("effort_person_months" if k == "months" else k): v for k, v in selected.items()}, "stress": [{("effort_person_months" if k == "months" else k): v for k, v in row.items()} for row in stress], "owners": waves}, schema={"type": "object", "properties": {"brief": {"type": "string", "maxLength": 1200}, "assumption": {"type": "string", "maxLength": 500}, "validation_milestone": {"type": "string", "maxLength": 500}}, "required": ["brief", "assumption", "validation_milestone"], "additionalProperties": False})
        return model_brief
