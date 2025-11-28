import os
import json
from datetime import datetime

from src.agents.data_agent import run_data_agent
from src.agents.planner import Planner
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import Evaluator
from src.agents.creative_generator import CreativeGenerator


class Orchestrator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.output_path = cfg.get("output_path", "reports")
        os.makedirs(self.output_path, exist_ok=True)

    def run(self, query):
        print("🔹 Starting Orchestrator...")
        print(f"🔹 Query received: {query}")

        # 1. Planner Agent
        planner = Planner(self.cfg)
        plan = planner.create_plan(query)
        print("🔹 Planner generated plan:", plan)

        # 2. Data Agent
        data_path = self.cfg["data_path"]
        summary, df = run_data_agent(data_path, use_sample=self.cfg.get("use_sample_data", True))
        print("🔹 Data summary loaded.")

        # 3. Insight Agent
        insight_agent = InsightAgent(self.cfg)
        hypotheses = insight_agent.generate_hypotheses(df, plan)
        print("🔹 Insight Agent generated hypotheses.")

        # 4. Evaluator Agent
        evaluator = Evaluator(self.cfg)
        validated = evaluator.validate(hypotheses, df)
        print("🔹 Evaluator validated hypotheses.")

        # 5. Creative Generator
        creative_gen = CreativeGenerator(self.cfg)
        creatives = creative_gen.generate(df, validated)
        print("🔹 Creative Generator produced ideas.")

        # 6. Save Outputs
        timestamp = datetime.utcnow().isoformat()

        insights_out = {
            "query": query,
            "timestamp": timestamp,
            "hypotheses": validated,
            "data_summary": summary
        }

        creatives_out = {
            "query": query,
            "timestamp": timestamp,
            "creatives": creatives
        }

        # ---- FIX: WRITE FILES IN UTF-8 ----
        with open(os.path.join(self.output_path, "insights.json"), "w", encoding="utf-8") as f:
            json.dump(insights_out, f, indent=2, ensure_ascii=False)

        with open(os.path.join(self.output_path, "creatives.json"), "w", encoding="utf-8") as f:
            json.dump(creatives_out, f, indent=2, ensure_ascii=False)

        with open(os.path.join(self.output_path, "report.md"), "w", encoding="utf-8") as f:
            f.write("# 📊 Kasparro Agent Report\n\n")
            f.write(f"### Query: {query}\n\n")
            f.write("## 🧠 Validated Hypotheses\n")
            for h in validated:
                title = h.get("title", "Untitled")
                conf = h.get("confidence", "N/A")
                f.write(f"- **{title}** (confidence={conf})\n")

        print("✅ Outputs saved in /reports")
        print("🎉 Orchestration complete!")
