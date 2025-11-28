from src.agents.evaluator import Evaluator
import pandas as pd

def test_evaluator_basic():
    # Create sample dataset (14 days)
    df = pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=14),
        "clicks": [10] * 14,
        "impressions": [1000] * 14,
        "spend": [100] * 14,
        "revenue": [300] * 14
    })

    df["ctr_calc"] = df["clicks"] / df["impressions"] * 100
    df["roas_calc"] = df["revenue"] / df["spend"]
    df["cpc"] = df["spend"] / df["clicks"]
    df["cpm"] = df["spend"] / df["impressions"] * 1000

    evaluator = Evaluator({"confidence_min": 0.6})

    sample_hypothesis = [{
        "title": "CTR Drop Detected",
        "metric": "ctr",
        "description": "CTR decreased over period"
    }]

    validated = evaluator.validate(sample_hypothesis, df)

    # Assert output list exists
    assert isinstance(validated, list)
    # Assert hypothesis has confidence score
    assert "confidence" in validated[0]
