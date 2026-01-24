"""
Browser Agent - Automated browser actions using Browser Use API
Handles social media posting, profile updates, and web interactions
"""

import os
import json
import logging
import requests
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BrowserTask:
    """A task to be executed by the browser agent"""
    task_id: str
    task_type: str  # post, update_profile, navigate, scrape
    platform: str   # linkedin, facebook, twitter, instagram
    action: str     # The action description
    data: Dict[str, Any] = None
    status: str = "pending"
    result: Dict = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class BrowserAgent:
    """
    Browser automation agent using Browser Use API.
    Executes web tasks autonomously.
    """
    
    BROWSER_USE_API = "https://api.browser-use.com/v1"
    
    def __init__(self):
        self.api_key = os.getenv("BROWSER_USE_API_KEY")
        if not self.api_key:
            logger.warning("BROWSER_USE_API_KEY not found")
        
        self.task_queue: List[BrowserTask] = []
        self.completed_tasks: List[BrowserTask] = []
        
        # Social media URLs from env
        self.platforms = {
            "linkedin": os.getenv("LINKEDIN_URL", "https://www.linkedin.com/in/lazy-larry-344631373/"),
            "facebook": os.getenv("FACEBOOK_URL", "https://www.facebook.com/profile.php?id=61578065763242"),
            "twitter": os.getenv("TWITTER_URL", "https://x.com/lazylarries"),
        }
    
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _execute_browser_task(self, task: BrowserTask) -> Dict:
        """Execute a browser task via Browser Use API"""
        
        if not self.api_key:
            return {"error": "Browser Use API key not configured"}
        
        # Build the task instruction
        instruction = self._build_instruction(task)
        
        payload = {
            "task": instruction,
            "browser": "chromium",
            "headless": True,
            "timeout": 120,
        }
        
        try:
            response = requests.post(
                f"{self.BROWSER_USE_API}/tasks",
                headers=self._headers(),
                json=payload,
                timeout=180
            )
            
            if response.status_code >= 400:
                logger.error(f"Browser Use API error: {response.text}")
                return {"error": response.text, "status_code": response.status_code}
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Browser task failed: {e}")
            return {"error": str(e)}
    
    def _build_instruction(self, task: BrowserTask) -> str:
        """Build natural language instruction for browser agent"""
        
        if task.task_type == "post":
            return f"""
Go to {self.platforms.get(task.platform, task.platform)}.
If not logged in, the session should already be authenticated.
Create a new post with the following content:

{task.data.get('content', '')}

After posting, take a screenshot and return the post URL.
"""
        
        elif task.task_type == "update_profile":
            return f"""
Go to {self.platforms.get(task.platform, task.platform)}/edit (or the profile edit section).
Update the following fields:
{json.dumps(task.data, indent=2)}

Save the changes and take a screenshot.
"""
        
        elif task.task_type == "navigate":
            return f"""
Navigate to: {task.data.get('url', '')}
{task.data.get('additional_instructions', '')}
Take a screenshot of the page.
"""
        
        else:
            return task.action
    
    def queue_post(self, platform: str, content: str, media: List[str] = None) -> BrowserTask:
        """Queue a social media post"""
        task = BrowserTask(
            task_id=f"POST_{platform}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            task_type="post",
            platform=platform,
            action=f"Post content to {platform}",
            data={
                "content": content,
                "media": media or [],
            }
        )
        self.task_queue.append(task)
        logger.info(f"Queued post for {platform}: {content[:50]}...")
        return task
    
    def queue_profile_update(self, platform: str, updates: Dict) -> BrowserTask:
        """Queue a profile update"""
        task = BrowserTask(
            task_id=f"PROFILE_{platform}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            task_type="update_profile",
            platform=platform,
            action=f"Update profile on {platform}",
            data=updates
        )
        self.task_queue.append(task)
        return task
    
    def execute_queue(self) -> Dict[str, Any]:
        """Execute all queued tasks"""
        results = {
            "executed": 0,
            "success": 0,
            "failed": 0,
            "tasks": [],
        }
        
        while self.task_queue:
            task = self.task_queue.pop(0)
            task.status = "running"
            
            logger.info(f"Executing task: {task.task_id}")
            result = self._execute_browser_task(task)
            
            if "error" in result:
                task.status = "failed"
                task.result = result
                results["failed"] += 1
            else:
                task.status = "completed"
                task.result = result
                results["success"] += 1
            
            results["executed"] += 1
            results["tasks"].append({
                "task_id": task.task_id,
                "platform": task.platform,
                "status": task.status,
                "result": task.result,
            })
            
            self.completed_tasks.append(task)
        
        return results
    
    def get_platform_url(self, platform: str) -> str:
        """Get the URL for a platform"""
        return self.platforms.get(platform, "")
    
    def create_social_content_batch(self) -> List[Dict]:
        """
        Generate a batch of social content for all platforms.
        Returns ready-to-post content.
        """
        
        launch_content = {
            "linkedin": """🚀 Excited to announce: AutonomaX Mastery Pack is LIVE!

After months of building automation systems, I've packaged everything into one comprehensive bundle.

What's inside:
✅ 50+ Zen Art Printables (Commercial License)
✅ Creator Launch Templates
✅ Platform Playbooks (Shopify, Etsy, Fiverr)
✅ 50+ Automation SOPs
✅ Notion Revenue Dashboard
✅ AI Prompt Library

Value: $2,847 → Your Price: $497

Perfect for solopreneurs ready to build automated income streams.

🔗 Link in comments

#Automation #PassiveIncome #DigitalProducts #Entrepreneurship #SideHustle""",

            "twitter": """🚀 Just launched: AutonomaX Mastery Pack

Everything you need to build automated income:
• 50+ Zen Art designs
• Launch templates
• Platform playbooks
• Automation SOPs
• Revenue dashboard

$2,847 value → $497

Link in bio 🔗

#buildinpublic #passiveincome #automation""",

            "facebook": """🎉 Big announcement!

I've been working on something special - the AutonomaX Mastery Pack is now available!

This is the complete system I use to build and manage automated income streams. Everything from digital art collections to launch templates to automation workflows.

What you get:
🎨 50+ Zen Art Printables
📋 Creator Launch Templates
📚 Platform Playbooks
⚙️ 50+ Automation SOPs
📊 Notion Revenue Dashboard
🤖 100+ AI Prompts

Total value: $2,847
Launch price: $497

If you've been wanting to start building passive income, this is your chance.

Drop a 🚀 if you want the link!""",

            "instagram": """🚀 IT'S LIVE!

AutonomaX Mastery Pack - your complete system for automated income.

What's inside:
✨ 50+ Zen Art Designs
📦 Launch Templates
📚 Platform Playbooks
⚙️ Automation SOPs
📊 Revenue Dashboard
🤖 AI Prompts

$2,847 value → $497

Link in bio 🔗

.
.
.
#automation #passiveincome #digitalproducts #sidehustle #entrepreneur #solopreneur #workfromhome #onlinebusiness #contentcreator #makemoneyonline""",
        }
        
        return [
            {"platform": platform, "content": content}
            for platform, content in launch_content.items()
        ]


# Pre-built social posts for immediate deployment
LAUNCH_POSTS = {
    "linkedin": {
        "content": """🚀 Excited to announce: AutonomaX Mastery Pack is LIVE!

After months of building automation systems, I've packaged everything into one comprehensive bundle.

What's inside:
✅ 50+ Zen Art Printables (Commercial License)
✅ Creator Launch Templates  
✅ Platform Playbooks (Shopify, Etsy, Fiverr)
✅ 50+ Automation SOPs
✅ Notion Revenue Dashboard
✅ AI Prompt Library

Value: $2,847 → Your Price: $497

Perfect for solopreneurs ready to build automated income streams.

#Automation #PassiveIncome #DigitalProducts #Entrepreneurship""",
        "url": "https://www.linkedin.com/in/lazy-larry-344631373/",
    },
    "twitter": {
        "content": """🚀 Just launched: AutonomaX Mastery Pack

Everything for automated income:
• 50+ Zen Art designs
• Launch templates
• Platform playbooks  
• Automation SOPs
• Revenue dashboard

$2,847 value → $497

#buildinpublic #passiveincome""",
        "url": "https://x.com/lazylarries",
    },
    "facebook": {
        "content": """🎉 Big announcement! The AutonomaX Mastery Pack is now available!

Complete system for automated income streams:
🎨 50+ Zen Art Printables
📋 Creator Launch Templates
📚 Platform Playbooks
⚙️ 50+ Automation SOPs
📊 Notion Revenue Dashboard

Total value: $2,847 | Launch price: $497

Drop a 🚀 if you want the link!""",
        "url": "https://www.facebook.com/profile.php?id=61578065763242",
    },
}


def generate_social_content_files(output_dir: str = None) -> Dict[str, str]:
    """
    Generate social content as files ready for manual posting.
    Returns paths to generated files.
    """
    import os
    from pathlib import Path
    
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "marketing_outputs", "social_posts")
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    files = {}
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    for platform, data in LAUNCH_POSTS.items():
        filename = f"{platform}_post_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w") as f:
            f.write(f"PLATFORM: {platform.upper()}\n")
            f.write(f"URL: {data['url']}\n")
            f.write(f"GENERATED: {datetime.utcnow().isoformat()}\n")
            f.write("="*50 + "\n\n")
            f.write(data['content'])
        
        files[platform] = filepath
        logger.info(f"Generated social content: {filepath}")
    
    return files
