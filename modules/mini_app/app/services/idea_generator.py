import openai
from typing import List, Dict, Any
from ..config import settings
from ..models import CommercialIdea
import logging

logger = logging.getLogger(__name__)
openai.api_key = settings.openai_api_key

class CommercialIdeaGenerator:
    async def generate_ideas(self, niche: str, focus: str, count: int) -> List[CommercialIdea]:
        ideas = []
        prompt = f"""
        Generate {count} YouTube video ideas for the niche '{niche}' with a strong commercial focus on '{focus}'.
        For each idea, provide:
        1. A catchy Title.
        2. A brief Description (1-2 sentences).
        3. A Commercial Angle (e.g., affiliate products, sponsorship type, high ad revenue potential).
        4. An estimated CPM range (e.g., '$X-$Y') if applicable for '{focus}'.
        5. A list of 3-5 relevant Keywords.

        Format each idea as a distinct block. Example:
        Title: Top 5 High-Ticket Affiliate Programs for {niche} Creators
        Description: Discover lucrative affiliate programs that can significantly boost your income.
        Commercial Angle: Promoting high-commission affiliate products.
        Estimated CPM Range: $10-$25 (due to finance/business focus)
        Keywords: affiliate marketing, high ticket, {niche}, passive income, creator economy
        ---
        """
        try:
            response = openai.Completion.create(
                engine="text-davinci-003", # Or a newer model if available and configured
                prompt=prompt,
                max_tokens=150 * count, # Adjust as needed
                n=1,
                stop="---"
            )
            content = response.choices[0].text.strip()
            # This parsing is basic; a more robust solution would use structured output from the LLM if possible, or better regex.
            raw_ideas = content.split('---')
            for raw_idea in raw_ideas:
                if raw_idea.strip():
                    # Basic parsing, assuming structure. Needs improvement for robustness.
                    lines = [line.strip() for line in raw_idea.strip().split('\n') if line.strip()]
                    if len(lines) >= 3: # Ensure at least title, desc, angle
                        ideas.append(CommercialIdea(title=lines[0].replace("Title:","").strip(), description=lines[1].replace("Description:","").strip(), commercial_angle=lines[2].replace("Commercial Angle:","").strip()))
        except Exception as e:
            logger.error(f"Error generating commercial ideas: {e}")
            # Fallback or error handling
            ideas.append(CommercialIdea(title=f"Error Generating Idea for {niche}", description=str(e), commercial_angle="Error"))
        return ideas[:count]