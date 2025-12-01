import pandas as pd
import os
from src.utils.schema_validator import SchemaValidator, SchemaValidationError
import yaml


def load_schema(schema_path):
    with open(schema_path, "r") as f:
        return yaml.safe_load(f)


def load_data(path):
    try:
        df = pd.read_csv(path)
        print(f"🔹 Data Agent: Loaded {len(df)} rows.")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ CSV file not found at path: {path}")
    except Exception as e:
        raise RuntimeError(f"❌ Error loading CSV: {e}")


def compute_basic_metrics(df):
    """
    Adds calculated metrics safely (CTR, CPC, CPM, ROAS)
    """
    df = df.copy()

    # Avoid divide-by-zero errors
    df["ctr_calc"] = df.apply(
        lambda row: (row["clicks"] / row["impressions"] * 100)
        if row["impressions"] > 0 else 0,
        axis=1
    )

    df["cpc_calc"] = df.apply(
        lambda row: (row["spend"] / row["clicks"])
        if row["clicks"] > 0 else 0,
        axis=1
    )

    df["cpm_calc"] = df.apply(
        lambda row: (row["spend"] / row["impressions"] * 1000)
        if row["impressions"] > 0 else 0,
        axis=1
    )

    df["roas_calc"] = df.apply(
        lambda row: (row["revenue"] / row["spend"])
        if row["spend"] > 0 else 0,
        axis=1
    )

    return df


def summarize_data(df):
    """
    Returns summary info for logs & insights.json
    """
    return {
        "rows": len(df),
        "date_range": f"{df['date'].min()} → {df['date'].max()}",
        "avg_ctr": df["ctr_calc"].mean(),
        "avg_roas": df["roas_calc"].mean(),
    }


def run_data_agent(csv_path, use_sample=False):
    """
    Main Data Agent function (called from orchestrator)
    """

    # Select dataset
    path = csv_path

    # Load dataset
    df = load_data(path)

    # Load schema
    schema_file_path = "config/schema.yaml"
    schema_info = load_schema(schema_file_path)
    required_schema = schema_info["required_columns"]

    # Validate schema
    validator = SchemaValidator(required_schema)

    try:
        validator.validate(df)
        print("✔ Schema valid. Data summary created.")
    except SchemaValidationError as e:
        raise RuntimeError(f"❌ SCHEMA ERROR: {e}")

    # Compute metrics
    df = compute_basic_metrics(df)

    # Summary for insights.json
    summary = summarize_data(df)

    return summary, df
