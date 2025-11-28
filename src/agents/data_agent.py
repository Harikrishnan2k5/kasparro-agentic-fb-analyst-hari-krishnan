import pandas as pd
import numpy as np


# 1. Load CSV data
def load_data(path):
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        raise

    # Convert date column if exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df


# 2. Normalize CTR (some datasets store CTR as 0.02 instead of 2.0%)
def normalize_ctr(df):
    if 'ctr' in df.columns:
        median_ctr = df['ctr'].dropna().median()
        if median_ctr is not None and median_ctr < 0.5:  # likely ratio form
            df['ctr'] = df['ctr'] * 100.0
    return df


# 3. Compute derived metrics: CTR, CPC, CPM, ROAS
def compute_derived(df):
    df = df.copy()

    df['impressions'] = pd.to_numeric(df.get('impressions', 0)).fillna(0)
    df['clicks'] = pd.to_numeric(df.get('clicks', 0)).fillna(0)
    df['spend'] = pd.to_numeric(df.get('spend', 0)).fillna(0)
    df['revenue'] = pd.to_numeric(df.get('revenue', 0)).fillna(0)

    df['ctr_calc'] = np.where(df['impressions'] > 0, df['clicks'] / df['impressions'] * 100, np.nan)
    df['cpc'] = np.where(df['clicks'] > 0, df['spend'] / df['clicks'], np.nan)
    df['cpm'] = np.where(df['impressions'] > 0, df['spend'] / df['impressions'] * 1000, np.nan)
    df['roas_calc'] = np.where(df['spend'] > 0, df['revenue'] / df['spend'], np.nan)

    return df


# 4. Create simple dataset summary
def summarize(df, top_n=5):
    summary = {
        "rows": int(df.shape[0]),
        "date_min": str(df['date'].min().date()) if 'date' in df.columns else None,
        "date_max": str(df['date'].max().date()) if 'date' in df.columns else None,
        "top_campaigns_by_spend": {}
    }

    if "campaign_name" in df.columns:
        summary["top_campaigns_by_spend"] = (
            df.groupby("campaign_name")["spend"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
            .to_dict()
        )

    return summary


# MAIN FUNCTION (called by orchestrator)
def run_data_agent(path, use_sample=True):
    print("🔹 Loading dataset from:", path)

    df = load_data(path)
    df = normalize_ctr(df)
    df = compute_derived(df)
    summary = summarize(df)

    print("🔹 Data Agent: Loaded", summary["rows"], "rows.")
    return summary, df
