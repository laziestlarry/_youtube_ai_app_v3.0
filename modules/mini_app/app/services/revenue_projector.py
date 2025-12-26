from ..models import RevenueProjection

class SimpleRevenueProjector:
    async def project(self, title: str, niche: str, estimated_views: int, estimated_cpm: float) -> RevenueProjection:
        # Simplified ad revenue projection
        projected_ad_revenue = (estimated_views / 1000) * estimated_cpm

        return RevenueProjection(
            title=title,
            projected_ad_revenue=round(projected_ad_revenue, 2),
            notes=f"Projection for '{niche}' based on {estimated_views:,} views and ${estimated_cpm:.2f} CPM. Does not include other monetization."
        )