import numpy as np

class Evaluator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.min_conf = cfg.get("confidence_min", 0.6)

    def compute_change(self, prev, last):
        """Returns percent change (negative means drop)"""
        if prev == 0 or np.isnan(prev) or np.isnan(last):
            return 0
        return (last - prev) / prev

    def eval_ctr(self, prev7, last7):
        prev = prev7["ctr_calc"].mean()
        last = last7["ctr_calc"].mean()
        change = self.compute_change(prev, last)
        if change < 0:
            return min(1.0, abs(change) * 5)
        return 0.3

    def eval_roas(self, prev7, last7):
        prev = prev7["roas_calc"].mean()
        last = last7["roas_calc"].mean()
        change = self.compute_change(prev, last)
        if change < 0:
            return min(1.0, abs(change) * 4)
        return 0.3

    def eval_cpc(self, prev7, last7):
        prev = prev7["cpc"].mean()
        last = last7["cpc"].mean()
        change = self.compute_change(prev, last)
        if change > 0:
            return min(1.0, abs(change) * 4)
        return 0.3

    def eval_cpm(self, prev7, last7):
        prev = prev7["cpm"].mean()
        last = last7["cpm"].mean()
        change = self.compute_change(prev, last)
        if change > 0:
            return min(1.0, abs(change) * 4)
        return 0.3

    def validate(self, hypotheses, df):
        df_sorted = df.sort_values("date")

        # If not enough rows → return as-is
        if df_sorted.shape[0] < 14:
            validated = []
            for h in hypotheses:
                h["confidence"] = 0.5
                validated.append(h)
            return validated

        # split time windows
        last7 = df_sorted.tail(7)
        prev7 = df_sorted.iloc[-14:-7]

        validated = []

        for h in hypotheses:
            metric = h.get("metric", "none")

            if metric == "ctr":
                conf = self.eval_ctr(prev7, last7)

            elif metric == "roas":
                conf = self.eval_roas(prev7, last7)

            elif metric == "cpc":
                conf = self.eval_cpc(prev7, last7)

            elif metric == "cpm":
                conf = self.eval_cpm(prev7, last7)

            else:
                conf = 0.5  # neutral

            # assign confidence
            h_out = dict(h)
            h_out["confidence"] = round(float(conf), 3)
            validated.append(h_out)

        return validated
