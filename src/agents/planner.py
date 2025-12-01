class Planner:
    def __init__(self, cfg):
        self.cfg = cfg

    # 1. Identify what the user wants
    def classify_query(self, query):
        q = query.lower()

        if "roas" in q or "return" in q or "revenue" in q:
            return "roas_analysis"

        if "ctr" in q or "click-through" in q or "click" in q:
            return "ctr_analysis"

        if "cpc" in q or "cost per click" in q:
            return "cpc_analysis"

        if "cpm" in q or "cost per thousand" in q:
            return "cpm_analysis"

        if "creative" in q or "ad copy" in q or "message" in q:
            return "creative_analysis"

        if "budget" in q or "scale" in q or "pause" in q:
            return "budget_optimization"

        if "anomaly" in q or "spike" in q or "drop" in q:
            return "anomaly_detection"

        # Default fallback
        return "general_analysis"

    # 2. Create a plan based on the intent
    def create_plan(self, query):
        intent = self.classify_query(query)

        plan = {
            "intent": intent,
            "steps": []
        }

        # Steps common to all analyses
        plan["steps"].append("load_data")
        plan["steps"].append("filter_time_window")
        plan["steps"].append("compute_metrics")

        # Intent-specific steps
        if intent in ["roas_analysis", "ctr_analysis", "cpc_analysis", "cpm_analysis", 
                      "anomaly_detection", "creative_analysis"]:
            plan["steps"].append("generate_hypotheses")
            plan["steps"].append("validate_hypotheses")

        if intent == "creative_analysis":
            plan["steps"].append("generate_creative_ideas")

        # Final report generation step
        plan["steps"].append("produce_report")

        return plan
