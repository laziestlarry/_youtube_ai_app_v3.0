"""
Growth Analytics Snapshot - Professional KPI Report.
Uses AnalyticsService for DNR and Slope calculation.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from modules.growth_engine_v1.app import SessionLocal
from modules.growth_engine_v1.analytics import AnalyticsService

def generate_report():
    print("📈 [AUTONOMAX] Growth Analytics Snapshot\n")
    db = SessionLocal()
    try:
        analytics = AnalyticsService(db)
        kpis = analytics.get_kpi_summary()
        series = analytics.get_chart_series()
        
        print(f"💰 Daily Net Revenue (DNR): ${kpis['dnr']:.2f} {kpis['currency']}")
        print(f"📉 7-Day DNR Slope: {kpis['slope']:.4f}")
        
        print("\n📊 [7-DAY REVENUE TREND]")
        for point in series['dnr']:
            bar = "█" * int(point['net'] / 100) if point['net'] > 0 else ""
            print(f"   {point['d']} | ${point['net']:8.2f} {bar}")
            
    finally:
        db.close()

if __name__ == "__main__":
    generate_report()
