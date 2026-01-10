from sqlalchemy.orm import Session
from sqlalchemy import func, select, text
from datetime import datetime, timedelta
from .models import GrowthLedgerEntry

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_dnr(self) -> float:
        """
        Calculate Daily Net Revenue (DNR) for today.
        DNR = Sum of CLEARED ledger entries for today.
        """
        today = datetime.utcnow().date()
        result = self.db.query(func.sum(GrowthLedgerEntry.amount_cents))\
            .filter(GrowthLedgerEntry.status == "CLEARED")\
            .filter(func.date(GrowthLedgerEntry.created_at) == today)\
            .scalar()
        
        return float(result or 0) / 100.0

    def get_slope(self) -> float:
        """
        Calculate the 7-day DNR Slope.
        Slope = (DNR_today - DNR_7d_ago) / 7
        """
        dnr_today = self.get_dnr()
        
        # Get DNR 7 days ago
        seven_days_ago = datetime.utcnow().date() - timedelta(days=7)
        dnr_7d_ago_cents = self.db.query(func.sum(GrowthLedgerEntry.amount_cents))\
            .filter(GrowthLedgerEntry.status == "CLEARED")\
            .filter(func.date(GrowthLedgerEntry.created_at) == seven_days_ago)\
            .scalar()
        
        dnr_7d_ago = float(dnr_7d_ago_cents or 0) / 100.0
        
        # Simple Linear Slope
        slope = (dnr_today - dnr_7d_ago) / 7.0
        return slope
        
    def get_kpi_summary(self) -> dict:
        return {
            "dnr": self.get_dnr(),
            "slope": self.get_slope(),
            "currency": "USD"
        }

    def get_chart_series(self) -> dict:
        """
        Returns time-series data for Vega-Lite charts.
        """
        # 1. DNR Trend (Last 7 Days)
        # For "Earliest Outcome", if we don't have enough data, we simulate a "startup curve" 
        # combined with real data so the chart isn't empty.
        
        dnr_data = []
        today = datetime.utcnow().date()
        
        # Fetch real daily aggregates
        rows = self.db.query(
            func.date(GrowthLedgerEntry.created_at).label("d"), 
            func.sum(GrowthLedgerEntry.amount_cents).label("net")
        ).filter(GrowthLedgerEntry.status == "CLEARED")\
         .group_by(func.date(GrowthLedgerEntry.created_at))\
         .all()
         
        real_map = {str(r.d): r.net/100.0 for r in rows}
        
        # Fill last 7 days (including today)
        for i in range(7):
            d = today - timedelta(days=6-i)
            # Use real data if exists, else 0 (or simulated startup noise if requested)
            val = real_map.get(str(d), 0.0)
            dnr_data.append({"d": str(d), "net": val})
            
        return {
            "dnr": dnr_data,
            "streams": self.get_stream_breakdown()
        }

    def get_stream_breakdown(self) -> list:
        """
        Group revenue by stream for today.
        """
        today = datetime.utcnow().date()
        rows = self.db.query(
            GrowthLedgerEntry.stream,
            func.sum(GrowthLedgerEntry.amount_cents).label("net")
        ).filter(GrowthLedgerEntry.status == "CLEARED")\
         .filter(func.date(GrowthLedgerEntry.created_at) == today)\
         .group_by(GrowthLedgerEntry.stream)\
         .all()
         
        return [
            {"date": str(today), "stream": r.stream or "UNKNOWN", "net": float(r.net)/100.0}
            for r in rows
        ]
