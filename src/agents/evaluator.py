import numpy as np
import pandas as pd

class Evaluator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.min_conf = cfg.get("confidence_min", 0.5)

    def _compute_confidence(self, delta_pct):
        """
        Turns delta% into a confidence score.
        Larger negative delta ⇒ higher confidence.
        """
        delta = abs(delta_pct)

        if delta >= 40:
            return 0.95
        elif delta >= 30:
            return 0.85
        elif delta >= 20:
            return 0.75
        elif delta >= 10:
            return 0.65
        return 0.55

    def _severity(self, delta_pct):
        """
        Qualitative severity based on magnitude of drop.
        """
        if delta_pct <= -40:
            return "critical"
        elif delta_pct <= -25:
            return "high"
        elif delta_pct <= -15:
            return "medium"
        return "low"

    def validate(self, hypotheses, df):
        """
        Takes hypotheses from InsightAgent and upgrades them with:
        - confidence
        - severity
        - statistical evidence
        """
        validated = []

        for h in hypotheses:
            # If hypothesis has no delta, it's a fallback hypothesis
            if "delta_pct" not in h:
                h["confidence"] = 0.4
                h["severity"] = "low"
                validated.append(h)
                continue

            delta = h["delta_pct"]

            # Confidence score
            conf = self._compute_confidence(delta)

            # Severity label
            sev = self._severity(delta)

            # Statistical strength: variance check
            metric = h.get("metric", "roas")
            metric_series = df[metric]

            variance = float(metric_series.var())
            std_dev = float(metric_series.std())

            evidence = h.get("evidence", {})
            evidence["variance"] = variance
            evidence["std_dev"] = std_dev
            evidence["sample_size"] = len(metric_series)

            upgraded = {
                **h,
                "confidence": round(conf, 3),
                "severity": sev,
                "evidence": evidence
            }

            # Keep only meaningful hypotheses
            if conf >= self.min_conf:
                validated.append(upgraded)

        return validated
