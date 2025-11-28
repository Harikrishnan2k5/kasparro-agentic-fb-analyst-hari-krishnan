class CreativeGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def find_low_ctr_campaigns(self, df, top_n=3):
        """Find lowest CTR campaigns for improvement."""
        if "campaign_name" not in df.columns:
            return []
        ctr_means = (
            df.groupby("campaign_name")["ctr_calc"]
            .mean()
            .sort_values()
            .head(top_n)
        )
        return list(ctr_means.index)

    def generate_creative_set(self, campaign_name):
        """Generate creative ideas based on common eCommerce patterns."""
        return {
            "campaign": campaign_name,
            "ideas": [
                {
                    "headline": "Limited Time Offer — Up to 50% Off!",
                    "primary_text": "Hurry! Grab your favorites before the sale ends.",
                    "cta": "Shop Now"
                },
                {
                    "headline": "🔥 Trending Product People Love!",
                    "primary_text": "Don’t miss out — thousands sold this month!",
                    "cta": "Buy Now"
                },
                {
                    "headline": "⚡ New Arrival Just Dropped!",
                    "primary_text": "Stylish, comfortable, and made for everyday wear.",
                    "cta": "Explore Collection"
                },
                {
                    "headline": "Why Wait? Your Perfect Fit Is Here",
                    "primary_text": "Special launch pricing for a short time only!",
                    "cta": "Grab Yours"
                }
            ]
        }

    def generate(self, df, validated_hypotheses):
        """Generate creatives for campaigns with low CTR or flagged insights."""
        low_ctr_campaigns = self.find_low_ctr_campaigns(df)

        suggestions = []

        for campaign in low_ctr_campaigns:
            ideas = self.generate_creative_set(campaign)
            suggestions.append(ideas)

        return suggestions
