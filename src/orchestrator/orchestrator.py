import os
import json
from datetime import datetime, timedelta, timezone

from src.agents.data_agent import run_data_agent
from src.agents.planner import Planner
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import Evaluator
from src.agents.creative_generator import CreativeGenerator


class Orchestrator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.output_path = cfg["paths"]["reports"]
        os.makedirs(self.output_path, exist_ok=True)

    def _get_ist_timestamp(self):
        IST = timezone(timedelta(hours=5, minutes=30))
        return datetime.now(IST).isoformat()

    def _create_run_folder(self):
        IST = timezone(timedelta(hours=5, minutes=30))
        ts = datetime.now(IST).strftime("run_%Y-%m-%d_%H-%M-%S")
        run_dir = os.path.join(self.output_path, ts)
        os.makedirs(run_dir, exist_ok=True)
        return run_dir, ts

    def run(self, query):
        print("🔹 Starting Orchestrator...")
        print(f"🔹 Query received: {query}")

        run_dir, run_id = self._create_run_folder()
        log_file = os.path.join(run_dir, "logs.txt")

        def log(msg):
            print(msg)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(msg + "\n")

        log(f"▶️ Run ID: {run_id}")
        log(f"▶️ Query: {query}")
        log("▶️ Status: Started\n")

        # ------------------------------- #
        # 1. Planner
        # ------------------------------- #
        planner = Planner(self.cfg)
        plan = planner.create_plan(query)
        log(f"📌 Planner Output: {plan}")

        # ------------------------------- #
        # 2. Data Agent
        # ------------------------------- #
        data_path = self.cfg["paths"]["data"]
        summary, df = run_data_agent(
            data_path,
            use_sample=self.cfg.get("use_sample_data", True)
        )
        log("📌 Data Agent: Data summary generated.")

        # ------------------------------- #
        # 3. Insight Agent
        # ------------------------------- #
        insight_agent = InsightAgent(self.cfg)
        hypotheses = insight_agent.generate_hypotheses(df, plan)
        log("📌 Insight Agent: Hypotheses generated.")

        # ------------------------------- #
        # 4. Evaluator
        # ------------------------------- #
        evaluator = Evaluator(self.cfg)
        validated = evaluator.validate(hypotheses, df)
        log("📌 Evaluator: Hypotheses validated.")

        # ------------------------------- #
        # 5. Creative Agent
        # ------------------------------- #
        creative_gen = CreativeGenerator(self.cfg)
        creatives = creative_gen.generate(df, validated)
        log("📌 Creative Agent: Creatives generated.")

        # ------------------------------- #
        # 6. Save Outputs
        # ------------------------------- #
        timestamp = self._get_ist_timestamp()

        insights_out = {
            "run_id": run_id,
            "query": query,
            "timestamp": timestamp,
            "hypotheses": validated,
            "data_summary": summary
        }

        creatives_out = {
            "run_id": run_id,
            "query": query,
            "timestamp": timestamp,
            "creatives": creatives
        }

        with open(os.path.join(run_dir, "insights.json"), "w", encoding="utf-8") as f:
            json.dump(insights_out, f, indent=2, ensure_ascii=False)

        with open(os.path.join(run_dir, "creatives.json"), "w", encoding="utf-8") as f:
            json.dump(creatives_out, f, indent=2, ensure_ascii=False)

        with open(os.path.join(run_dir, "report.md"), "w", encoding="utf-8") as f:
            f.write("# 📊 Kasparro Agent Report (IST)\n\n")
            f.write(f"### Run ID: {run_id}\n")
            f.write(f"### Timestamp: {timestamp}\n")
            f.write(f"### Query: {query}\n\n")
            f.write("## 🧠 Validated Hypotheses\n")
            for h in validated:
                title = h.get("title", "Untitled")
                conf = h.get("confidence", "N/A")
                f.write(f"- **{title}** (confidence={conf})\n")

        log("✔️ Outputs saved successfully")
        log(f"📁 Run folder created at: {run_dir}")
        log("🎉 Status: Completed")

        print("🎉 Orchestration complete!")
