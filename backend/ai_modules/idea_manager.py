from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from enum import Enum
import json
from database import get_db_connection

logger = logging.getLogger(__name__)
router = APIRouter()

class IdeaPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class IdeaStatus(str, Enum):
    BACKLOG = "backlog"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class Idea(BaseModel):
    id: str
    title: str
    description: str
    priority: IdeaPriority
    status: IdeaStatus
    category: str
    estimated_effort: float
    potential_impact: float
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str]
    tags: List[str]
    metrics: Dict[str, Any]

class IdeaRanking(BaseModel):
    idea_id: str
    score: float
    rank: int
    justification: str

class IdeaManager:
    def __init__(self):
        self.db = get_db_connection()

    async def get_ranked_ideas(self, limit: int = 10) -> List[IdeaRanking]:
        """Get ranked ideas based on priority, impact, and dependencies."""
        try:
            # Fetch ideas from database
            ideas = await self._fetch_ideas()
            
            # Calculate scores and rank ideas
            ranked_ideas = []
            for idea in ideas:
                score = self._calculate_idea_score(idea)
                ranked_ideas.append(IdeaRanking(
                    idea_id=idea.id,
                    score=score,
                    rank=0,  # Will be set after sorting
                    justification=self._generate_justification(idea, score)
                ))
            
            # Sort by score and assign ranks
            ranked_ideas.sort(key=lambda x: x.score, reverse=True)
            for i, idea in enumerate(ranked_ideas):
                idea.rank = i + 1
            
            return ranked_ideas[:limit]
        except Exception as e:
            logger.error(f"Error ranking ideas: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _calculate_idea_score(self, idea: Idea) -> float:
        """Calculate idea score based on multiple factors."""
        priority_weights = {
            IdeaPriority.CRITICAL: 1.0,
            IdeaPriority.HIGH: 0.8,
            IdeaPriority.MEDIUM: 0.5,
            IdeaPriority.LOW: 0.2
        }
        
        # Base score from priority
        score = priority_weights[idea.priority] * 100
        
        # Adjust for potential impact
        score += idea.potential_impact * 20
        
        # Adjust for effort (lower effort = higher score)
        effort_factor = 1 - (idea.estimated_effort / 100)
        score += effort_factor * 30
        
        # Adjust for dependencies (fewer dependencies = higher score)
        dependency_factor = 1 - (len(idea.dependencies) / 10)
        score += dependency_factor * 20
        
        return min(100, max(0, score))

    def _generate_justification(self, idea: Idea, score: float) -> str:
        """Generate justification for the idea's ranking."""
        justifications = []
        
        if idea.priority == IdeaPriority.CRITICAL:
            justifications.append("Critical priority item")
        elif idea.priority == IdeaPriority.HIGH:
            justifications.append("High priority item")
            
        if idea.potential_impact > 0.8:
            justifications.append("High potential impact")
        elif idea.potential_impact > 0.5:
            justifications.append("Moderate potential impact")
            
        if len(idea.dependencies) == 0:
            justifications.append("No dependencies")
        elif len(idea.dependencies) < 3:
            justifications.append("Few dependencies")
            
        return " | ".join(justifications)

    async def _fetch_ideas(self) -> List[Idea]:
        """Fetch ideas from database."""
        # TODO: Implement actual database fetch
        # For now, return sample data
        return [
            Idea(
                id="1",
                title="Implement AI Content Optimization",
                description="Add AI-powered content optimization features",
                priority=IdeaPriority.CRITICAL,
                status=IdeaStatus.BACKLOG,
                category="feature",
                estimated_effort=80.0,
                potential_impact=0.9,
                dependencies=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                assigned_to=None,
                tags=["ai", "optimization", "content"],
                metrics={"expected_roi": 2.5}
            ),
            # Add more sample ideas as needed
        ]

@router.get("/ranked-ideas", response_model=List[IdeaRanking])
async def get_ranked_ideas(limit: int = 10):
    """Get ranked ideas endpoint."""
    idea_manager = IdeaManager()
    return await idea_manager.get_ranked_ideas(limit) 