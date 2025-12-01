import pandas as pd

class InsightAgent:
    def __init__(self, cfg):
        self.cfg = cfg

    def generate_hypotheses(self, df, plan):
        """
        Produces data-driven hypotheses:
        - CTR drop
        - ROAS drop
        - Cost increase
        - Segment issues (country, platform, audience_type)
        """
        hypotheses = []

        # Last 7 days
        df["date"] = pd.to_datetime(df["date"])
        last7 = df[df["date"] >= df["date"].max() - pd.Timedelta(days=7)]
        prev7 = df[(df["date"] < df["date"].max() - pd.Timedelta(days=7)) &
                   (df["date"] >= df["date"].max() - pd.Timedelta(days=14))]

        if last7.empty or prev7.empty:
            return [{
                "title": "Insufficient data for time-window comparison",
                "confidence": 0.2,
                "impact": "low",
                "evidence": {}
            }]

        # Compute metrics
        metrics = ["ctr", "roas", "spend", "impressions", "clicks"]
        for m in metrics:
            last = last7[m].mean()
            prev = prev7[m].mean()

            if prev == 0:
                continue

            delta = ((last - prev) / prev) * 100

            # ROAS drop hypothesis
            if m == "roas" and delta < -10:
                hypotheses.append({
                    "title": "ROAS dropped significantly",
                    "metric": "roas",
                    "delta_pct": round(delta, 2),
                    "impact": "high" if delta < -20 else "medium",
                    "evidence": {
                        "last_7d": round(last, 3),
                        "prev_7d": round(prev, 3)
                    }
                })

            # CTR drop hypothesis
            if m == "ctr" and delta < -10:
                hypotheses.append({
                    "title": "CTR dropped significantly",
                    "metric": "ctr",
                    "delta_pct": round(delta, 2),
                    "impact": "medium",
                    "evidence": {
                        "last_7d": round(last, 4),
                        "prev_7d": round(prev, 4)
                    }
                })

        # Segment-level analysis
        segments = ["country", "platform", "audience_type"]

        for seg in segments:
            group_last = last7.groupby(seg)["roas"].mean()
            group_prev = prev7.groupby(seg)["roas"].mean()

            for key in group_last.index:
                if key in group_prev:
                    diff = group_last[key] - group_prev[key]
                    pct = (diff / group_prev[key]) * 100 if group_prev[key] != 0 else 0

                    if pct < -15:  # segment-level drop
                        hypotheses.append({
                            "title": f"ROAS dropped significantly in segment: {seg} = {key}",
                            "segment": seg,
                            "segment_value": key,
                            "delta_pct": round(pct, 2),
                            "impact": "high",
                            "evidence": {
                                "last_7d": round(group_last[key], 3),
                                "prev_7d": round(group_prev[key], 3)
                            }
                        })

        # If nothing triggered
        if not hypotheses:
            hypotheses.append({
                "title": "No major performance changes detected",
                "confidence": 0.5,
                "impact": "low",
                "evidence": {}
            })

        return hypotheses
