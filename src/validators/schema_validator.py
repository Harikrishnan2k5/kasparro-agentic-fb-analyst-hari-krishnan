import pandas as pd
from typing import List

REQUIRED_COLUMNS = [
    "campaign_name",
    "adset_name",
    "date",
    "spend",
    "impressions",
    "clicks",
    "ctr",
    "purchases",
    "revenue",
    "roas",
    "creative_type",
    "creative_message",
    "audience_type",
    "platform",
    "country"
]

NUMERIC_COLUMNS = ["spend", "impressions", "clicks", "purchases", "revenue", "roas", "ctr"]

def validate_schema(df: pd.DataFrame) -> List[str]:
    errors = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"missing_columns: {missing}")
        return errors

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                errors.append(f"column_not_numeric: {col}")

    if df.shape[0] == 0:
        errors.append("empty_dataframe")

    return errors
