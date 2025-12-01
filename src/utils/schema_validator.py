import pandas as pd

class SchemaValidationError(Exception):
    pass

class SchemaValidator:
    def __init__(self, required_schema: dict):
        self.required_schema = required_schema

    def validate(self, df: pd.DataFrame):
        errors = []

        # Check required columns
        missing_cols = [col for col in self.required_schema.keys() if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")

        # Check column types (numeric vs string)
        for col, expected_type in self.required_schema.items():
            if col in df.columns:
                if expected_type == "numeric" and not pd.api.types.is_numeric_dtype(df[col]):
                    errors.append(f"Column '{col}' should be numeric.")
                if expected_type == "string" and not pd.api.types.is_string_dtype(df[col]):
                    errors.append(f"Column '{col}' should be string.")

        if errors:
            raise SchemaValidationError(" | ".join(errors))

        return True
