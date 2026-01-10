from sqlalchemy.orm import Session
from .models import BusinessMission
from typing import Dict, Any, Optional

class StrategyService:
    def __init__(self, db: Session):
        self.db = db

    def get_mission(self) -> Optional[BusinessMission]:
        return self.db.query(BusinessMission).first()

    def update_mission(self, vision: str, values: Dict[str, Any], north_star: str = "daily_net_revenue"):
        mission = self.get_mission()
        if not mission:
            mission = BusinessMission(vision=vision, values=values, north_star_metric=north_star)
            self.db.add(mission)
        else:
            mission.vision = vision
            mission.values = values
            mission.north_star_metric = north_star
        self.db.commit()
        self.db.refresh(mission)
        return mission

    def get_strategic_guidance(self):
        mission = self.get_mission()
        if not mission:
            return "No strategic vision defined. Defaulting to revenue maximization."
        
        return {
            "vision": mission.vision,
            "north_star": mission.north_star_metric,
            "values": mission.values,
            "guidance": f"All actions must align with: {mission.vision}. Primary objective: Optimize {mission.north_star_metric}."
        }
