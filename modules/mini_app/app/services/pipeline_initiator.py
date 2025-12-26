import requests
import logging
from ..config import settings
from ..models import CommercialIdea

logger = logging.getLogger(__name__)

class MainPipelineInitiator:
    async def initiate(self, idea: CommercialIdea, target_platform_url: str = None) -> dict:
        main_platform_url = target_platform_url or settings.main_platform_url
        initiation_endpoint = f"{main_platform_url}/api/v1/initiate-video-from-brief" # Example endpoint

        payload = {
            "title": idea.title,
            "topic": idea.description, # Using description as topic for simplicity
            "category": idea.keywords[0] if idea.keywords else "general", # Use first keyword as category
            "commercial_angle": idea.commercial_angle,
            "source": "youtube-income-commander-mini",
            "priority_score": 8 # Example priority
        }

        try:
            response = requests.post(initiation_endpoint, json=payload, timeout=10)
            response.raise_for_status() # Raise an exception for HTTP errors
            logger.info(f"Successfully initiated pipeline on main platform for: {idea.title}")
            return {"status": "success", "message": "Pipeline initiated on main platform.", "details": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to initiate pipeline on main platform for {idea.title}: {e}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"An unexpected error occurred during pipeline initiation: {e}")
            return {"status": "error", "message": "An unexpected error occurred."}