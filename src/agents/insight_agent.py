import numpy as np

class InsightAgent:
    def __init__(self, cfg):
        self.cfg = cfg

    # Generate hypotheses (data-driven insights)
    def generate_hypotheses(self, df, plan):

        hypotheses = []

        # Ensure data is sorted by date
        df_sorted = df.sort_values("date")

        # 🔹 Case 1: Not enough data
        if df_sorted.shape[0] < 14:
            hypotheses.append({
                "title": "Insufficient Data",
                "description": "Less than 14 days of data — cannot evaluate trends accurately.",
                "metric": "none"
            })
            return hypotheses

        # Split last 7 days vs previous 7 days
        last7 = df_sorted.tail(7)
        prev7 = df_sorted.iloc[-14:-7]

        # --- CTR hypothesis ---
        mean_ctr_last = last7["ctr_calc"].mean()
        mean_ctr_prev = prev7["ctr_calc"].mean()

        if mean_ctr_prev > 0 and mean_ctr_last < mean_ctr_prev * (1 - self.cfg["thresholds"]["ctr_drop_pct"] / 100):
            hypotheses.append({
                "title": "CTR Drop Detected",
                "description": f"CTR dropped from {mean_ctr_prev:.2f}% to {mean_ctr_last:.2f}%.",
                "metric": "ctr"
            })

        # --- ROAS hypothesis ---
        mean_roas_last = last7["roas_calc"].mean()
        mean_roas_prev = prev7["roas_calc"].mean()

        if mean_roas_prev > 0 and mean_roas_last < mean_roas_prev * (1 - self.cfg["thresholds"]["roas_drop_pct"] / 100):
            hypotheses.append({
                "title": "ROAS Drop Detected",
                "description": f"ROAS dropped from {mean_roas_prev:.2f} to {mean_roas_last:.2f}.",
                "metric": "roas"
            })

        # --- CPC hypothesis ---
        if "cpc" in df.columns:
            cpc_last = last7["cpc"].mean()
            cpc_prev = prev7["cpc"].mean()

            if cpc_prev > 0 and cpc_last > cpc_prev * 1.10:
                hypotheses.append({
                    "title": "Higher CPC",
                    "description": f"CPC increased from {cpc_prev:.2f} to {cpc_last:.2f}.",
                    "metric": "cpc"
                })

        # --- CPM hypothesis ---
        if "cpm" in df.columns:
            cpm_last = last7["cpm"].mean()
            cpm_prev = prev7["cpm"].mean()

            if cpm_prev > 0 and cpm_last > cpm_prev * 1.10:
                hypotheses.append({
                    "title": "Higher CPM",
                    "description": f"CPM increased from {cpm_prev:.2f} to {cpm_last:.2f}.",
                    "metric": "cpm"
                })

        # If nothing found
        if len(hypotheses) == 0:
            hypotheses.append({
                "title": "No Major Changes Detected",
                "description": "Metrics stable compared to previous period.",
                "metric": "none"
            })

        return hypotheses
