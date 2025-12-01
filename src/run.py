import sys
import os
import argparse
import yaml

# Ensure project root is on PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator.orchestrator import Orchestrator


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="User query, e.g., 'Analyze ROAS drop last 7 days'")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    # Load config safely
    cfg = load_config(args.config) or {}

    # Override with sample flag
    if args.sample:
        cfg["use_sample_data"] = True

    # Start orchestrator
    orchestrator = Orchestrator(cfg)
    orchestrator.run(args.query)


if __name__ == "__main__":
    main()
