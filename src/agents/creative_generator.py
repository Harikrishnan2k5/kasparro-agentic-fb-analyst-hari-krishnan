# src/agents/creative_generator.py

import pandas as pd
import numpy as np

class CreativeGenerator:
    """
    V2 Creative Agent:
    - Reads validated hypotheses
    - Ties creatives directly to insight drivers
    - Uses segment-level diagnosis (low CTR, low ROAS groups)
    - Produces multiple creative directions:
        * Hook
        * Value prop
        * CTA
        * Format suggestion
    """

    def __init__(self, cfg):
        self.cfg = cfg

    def generate(self, df, validated_hypotheses):
        if df is None or df.empty:
            return []

        creatives = []

        # 1. Identify worst segments (helpful for creative targeting)
        worst_segments = self._find_worst_segments(df)

        for hypo in validated_hypotheses:
            title = hypo.get("title", "")
            evidence = hypo.get("evidence", {})
            confidence = hypo.get("confidence", 0.0)

            # Generate 3 creative directions for each hypothesis
            ideas = self._generate_creative_directions(title, evidence, worst_segments)

            creatives.append({
                "hypothesis": title,
                "confidence": confidence,
                "evidence": evidence,
                "target_segments": worst_segments,
                "creative_directions": ideas
            })

        return creatives

    # ----------------------------------------------------------------------
    #  A. Identify performance-broken segments (low CTR / low ROAS groups)
    # ----------------------------------------------------------------------
    def _find_worst_segments(self, df):
        try:
            segment_cols = ["country", "platform", "creative_type"]

            segments = df.groupby(segment_cols).agg({
                "ctr": "mean",
                "roas": "mean",
                "clicks": "sum",
                "spend": "sum"
            }).reset_index()

            # Rank segments by CTR + ROAS
            segments["score"] = (segments["ctr"].rank(pct=True) +
                                 segments["roas"].rank(pct=True)) / 2

            worst = segments.sort_values("score").head(3)

            return worst.to_dict(orient="records")

        except Exception:
            return []  # fallback gracefully

    # ----------------------------------------------------------------------
    #  B. Generate creative directions based on hypothesis & evidence
    # ----------------------------------------------------------------------
    def _generate_creative_directions(self, title, evidence, segments):
        ctr_delta = evidence.get("ctr_delta_pct", None)
        roas_delta = evidence.get("roas_delta_pct", None)
        top_issue = self._detect_issue(ctr_delta, roas_delta)

        ideas = []

        # Creative Direction 1: Hook-Based Fix
        ideas.append({
            "angle": "Hook Refresh",
            "problem_targeted": top_issue,
            "message": self._hook_based_message(top_issue),
            "cta": self._cta(top_issue),
            "format": self._format_suggestion(top_issue),
            "why_it_works": "Addressing the primary drop driver found in metrics."
        })

        # Creative Direction 2: Value Proposition Reinforcement
        ideas.append({
            "angle": "Value Proposition Deepening",
            "problem_targeted": top_issue,
            "message": self._value_prop_message(top_issue),
            "cta": self._cta(top_issue),
            "format": "Carousel or UGC review clip",
            "why_it_works": "Strengthens product trust after performance decline."
        })

        # Creative Direction 3: Segment-Specific Variant
        ideas.append({
            "angle": "Segment-Personalized Creative",
            "problem_targeted": "Segment with lowest performance metrics",
            "segment_used": segments[0] if segments else None,
            "message": self._segment_message(segments),
            "cta": "Try Now",
            "format": "Localized static + testimonial",
            "why_it_works": "Uses worst-performing audience group to rebuild CTR/ROAS."
        })

        return ideas

    # ----------------------------------------------------------------------
    # C. Helper logic for creative reasoning
    # ----------------------------------------------------------------------
    def _detect_issue(self, ctr_delta, roas_delta):
        if ctr_delta is not None and ctr_delta < -10:
            return "CTR Decline"
        if roas_delta is not None and roas_delta < -10:
            return "ROAS Decline"
        return "General Fatigue"

    def _hook_based_message(self, issue):
        if issue == "CTR Decline":
            return "Stop scrolling — see why 50,000+ customers chose us this week!"
        if issue == "ROAS Decline":
            return "Save more with our best-value bundles — limited time."
        return "A bold new look designed just for you."

    def _value_prop_message(self, issue):
        if issue == "CTR Decline":
            return "Experience comfort redefined — designed for all-day wear."
        if issue == "ROAS Decline":
            return "Get premium quality without premium prices — try the bestseller pack."
        return "A trusted choice — crafted with high-grade materials."

    def _cta(self, issue):
        if issue == "CTR Decline":
            return "View Styles"
        if issue == "ROAS Decline":
            return "Shop & Save"
        return "Explore Now"

    def _format_suggestion(self, issue):
        if issue == "CTR Decline":
            return "Short punchy 5–7 sec video"
        if issue == "ROAS Decline":
            return "Offer-banner + static hero image"
        return "Standard creative refresh"

    def _segment_message(self, segments):
        if not segments:
            return "Fresh look curated for you."

        top = segments[0]
        country = top.get("country", "your area")
        creative_type = top.get("creative_type", "visual")

        return f"Designed for {country} — optimized {creative_type} variant now live!"
