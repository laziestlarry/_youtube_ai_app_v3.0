from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from enum import Enum
import json

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
        pass

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
        from backend.database.models import ContentIdea
        from backend.core.database import AsyncSessionLocal
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            query = select(ContentIdea).order_by(ContentIdea.created_at.desc())
            result = await session.execute(query)
            db_ideas = result.scalars().all()
            
            # Map database models to Pydantic models
            ideas = []
            for db_idea in db_ideas:
                # Map priority (Int) to IdeaPriority (Enum)
                priority = IdeaPriority.MEDIUM
                if db_idea.priority >= 9: priority = IdeaPriority.CRITICAL
                elif db_idea.priority >= 7: priority = IdeaPriority.HIGH
                elif db_idea.priority >= 4: priority = IdeaPriority.MEDIUM
                else: priority = IdeaPriority.LOW
                
                # Map status string to IdeaStatus enum
                try:
                    status = IdeaStatus(db_idea.status)
                except ValueError:
                    status = IdeaStatus.BACKLOG
                
                ideas.append(Idea(
                    id=str(db_idea.id),
                    title=db_idea.title,
                    description=db_idea.description or "",
                    priority=priority,
                    status=status,
                    category=db_idea.category or "general",
                    estimated_effort=50.0, # Placeholder or map from metadata
                    potential_impact=db_idea.estimated_views / 10000.0 if db_idea.estimated_views else 0.5,
                    dependencies=[],
                    created_at=db_idea.created_at,
                    updated_at=db_idea.updated_at,
                    assigned_to=db_idea.created_by,
                    tags=json.loads(db_idea.keywords) if db_idea.keywords else [],
                    metrics={"estimated_revenue": db_idea.estimated_revenue}
                ))
            
            return ideas

@router.get("/ranked-ideas", response_model=List[IdeaRanking])
async def get_ranked_ideas(limit: int = 10):
    """Get ranked ideas endpoint."""
    idea_manager = IdeaManager()
    return await idea_manager.get_ranked_ideas(limit) 
