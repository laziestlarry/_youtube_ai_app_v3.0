"""
Social Media Executor - Direct API integration for social platforms
Handles LinkedIn, Twitter/X, Facebook, Instagram posting
"""

import os
import json
import logging
import requests
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SocialPost:
    """Social media post to be published"""
    platform: str
    content: str
    media_urls: List[str] = field(default_factory=list)
    link: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: str = "draft"
    post_id: Optional[str] = None
    post_url: Optional[str] = None


class LinkedInExecutor:
    """LinkedIn API integration"""
    
    API_BASE = "https://api.linkedin.com/v2"
    
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.api_key = os.getenv("LINKEDIN_API_KEY") or os.getenv("LINKEDIN_API-KEY")
        self.profile_url = os.getenv("LINKEDIN_URL", "").split("?")[0]
        
        # Extract URN from profile URL if possible
        self.user_urn = None
        
    def _headers(self, access_token: str = None) -> Dict[str, str]:
        token = access_token or self.api_key
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
    
    def get_profile(self, access_token: str = None) -> Dict:
        """Get LinkedIn profile info"""
        try:
            response = requests.get(
                f"{self.API_BASE}/me",
                headers=self._headers(access_token),
                timeout=30
            )
            return response.json()
        except Exception as e:
            logger.error(f"LinkedIn profile fetch failed: {e}")
            return {"error": str(e)}
    
    def create_post(self, content: str, access_token: str = None) -> Dict:
        """Create a LinkedIn post"""
        
        # Get user URN first
        profile = self.get_profile(access_token)
        if "error" in profile:
            return profile
        
        user_urn = f"urn:li:person:{profile.get('id')}"
        
        payload = {
            "author": user_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(
                f"{self.API_BASE}/ugcPosts",
                headers=self._headers(access_token),
                json=payload,
                timeout=30
            )
            
            if response.status_code >= 400:
                logger.error(f"LinkedIn post failed: {response.text}")
                return {"error": response.text}
            
            return response.json()
            
        except Exception as e:
            logger.error(f"LinkedIn post failed: {e}")
            return {"error": str(e)}


class TwitterExecutor:
    """Twitter/X API integration"""
    
    API_BASE = "https://api.twitter.com/2"
    
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.profile_url = os.getenv("TWITTER_URL", "https://x.com/lazylarries")
    
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
        }
    
    def create_tweet(self, content: str) -> Dict:
        """Create a tweet"""
        if not self.bearer_token:
            return {"error": "Twitter bearer token not configured"}
        
        payload = {"text": content}
        
        try:
            response = requests.post(
                f"{self.API_BASE}/tweets",
                headers=self._headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code >= 400:
                logger.error(f"Tweet failed: {response.text}")
                return {"error": response.text}
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Tweet failed: {e}")
            return {"error": str(e)}


class SocialMediaExecutor:
    """
    Unified social media executor.
    Coordinates posting across all platforms.
    """
    
    def __init__(self):
        self.linkedin = LinkedInExecutor()
        self.twitter = TwitterExecutor()
        
        self.post_queue: List[SocialPost] = []
        self.published_posts: List[SocialPost] = []
        self.execution_log: List[Dict] = []
        
        # Platform URLs for manual fallback
        self.platform_urls = {
            "linkedin": os.getenv("LINKEDIN_URL", ""),
            "facebook": os.getenv("FACEBOOK_URL", ""),
            "twitter": os.getenv("TWITTER_URL", ""),
            "instagram": "",  # Instagram requires Meta Business API
        }
    
    def queue_post(self, platform: str, content: str, media_urls: List[str] = None) -> SocialPost:
        """Queue a post for publishing"""
        post = SocialPost(
            platform=platform.lower(),
            content=content,
            media_urls=media_urls or [],
        )
        self.post_queue.append(post)
        logger.info(f"Queued {platform} post: {content[:50]}...")
        return post
    
    def publish_post(self, post: SocialPost) -> Dict:
        """Publish a single post"""
        
        post.status = "publishing"
        result = {"platform": post.platform, "status": "unknown"}
        
        try:
            if post.platform == "linkedin":
                api_result = self.linkedin.create_post(post.content)
                if "error" not in api_result:
                    post.status = "published"
                    post.post_id = api_result.get("id")
                    result["status"] = "success"
                    result["post_id"] = post.post_id
                else:
                    post.status = "failed"
                    result["status"] = "failed"
                    result["error"] = api_result.get("error")
            
            elif post.platform == "twitter":
                api_result = self.twitter.create_tweet(post.content)
                if "error" not in api_result:
                    post.status = "published"
                    post.post_id = api_result.get("data", {}).get("id")
                    result["status"] = "success"
                    result["post_id"] = post.post_id
                else:
                    post.status = "failed"
                    result["status"] = "failed"
                    result["error"] = api_result.get("error")
            
            else:
                # For platforms without API access, provide manual instructions
                post.status = "manual_required"
                result["status"] = "manual_required"
                result["url"] = self.platform_urls.get(post.platform, "")
                result["content"] = post.content
                result["instructions"] = f"Please post manually to {post.platform}"
        
        except Exception as e:
            post.status = "failed"
            result["status"] = "failed"
            result["error"] = str(e)
        
        self._log_execution(post, result)
        return result
    
    def execute_queue(self) -> Dict[str, Any]:
        """Execute all queued posts"""
        results = {
            "total": len(self.post_queue),
            "published": 0,
            "failed": 0,
            "manual_required": 0,
            "posts": [],
        }
        
        while self.post_queue:
            post = self.post_queue.pop(0)
            result = self.publish_post(post)
            
            if result["status"] == "success":
                results["published"] += 1
            elif result["status"] == "manual_required":
                results["manual_required"] += 1
            else:
                results["failed"] += 1
            
            results["posts"].append(result)
            self.published_posts.append(post)
        
        return results
    
    def _log_execution(self, post: SocialPost, result: Dict):
        """Log execution for audit"""
        self.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "platform": post.platform,
            "content_preview": post.content[:100],
            "status": post.status,
            "result": result,
        })
    
    def get_manual_posting_guide(self) -> Dict[str, Any]:
        """
        Generate a guide for manual posting with direct links and content.
        Use this when API access is not available.
        """
        
        posts = self._generate_launch_content()
        
        guide = {
            "generated_at": datetime.utcnow().isoformat(),
            "instructions": "Copy the content below and post to each platform manually.",
            "platforms": {},
        }
        
        for platform, content in posts.items():
            guide["platforms"][platform] = {
                "url": self.platform_urls.get(platform, ""),
                "content": content,
                "character_count": len(content),
            }
        
        return guide
    
    def _generate_launch_content(self) -> Dict[str, str]:
        """Generate launch content for all platforms"""
        return {
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

#Automation #PassiveIncome #DigitalProducts #Entrepreneurship #SideHustle""",

            "twitter": """🚀 Just launched: AutonomaX Mastery Pack

Everything you need for automated income:
• 50+ Zen Art designs
• Launch templates
• Platform playbooks
• Automation SOPs
• Revenue dashboard

$2,847 value → $497

#buildinpublic #passiveincome #automation""",

            "facebook": """🎉 Big announcement!

I've been working on something special - the AutonomaX Mastery Pack is now available!

This is the complete system I use to build and manage automated income streams.

What you get:
🎨 50+ Zen Art Printables
📋 Creator Launch Templates
📚 Platform Playbooks
⚙️ 50+ Automation SOPs
📊 Notion Revenue Dashboard
🤖 100+ AI Prompts

Total value: $2,847
Launch price: $497

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

#automation #passiveincome #digitalproducts #sidehustle #entrepreneur #solopreneur #workfromhome #onlinebusiness""",
        }
    
    def generate_content_files(self, output_dir: str) -> Dict[str, str]:
        """Generate content as text files for manual posting"""
        from pathlib import Path
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        posts = self._generate_launch_content()
        files = {}
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        for platform, content in posts.items():
            filename = f"{platform}_launch_{timestamp}.txt"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w") as f:
                f.write(f"PLATFORM: {platform.upper()}\n")
                f.write(f"POST URL: {self.platform_urls.get(platform, 'N/A')}\n")
                f.write(f"GENERATED: {datetime.utcnow().isoformat()}\n")
                f.write("="*60 + "\n\n")
                f.write("CONTENT TO POST:\n")
                f.write("-"*60 + "\n\n")
                f.write(content)
                f.write("\n\n" + "-"*60 + "\n")
                f.write(f"Character count: {len(content)}\n")
            
            files[platform] = filepath
        
        # Generate combined file
        combined_file = os.path.join(output_dir, f"ALL_PLATFORMS_{timestamp}.txt")
        with open(combined_file, "w") as f:
            f.write("AUTONOMAX LAUNCH - SOCIAL MEDIA CONTENT\n")
            f.write("="*60 + "\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n\n")
            
            for platform, content in posts.items():
                f.write(f"\n{'='*60}\n")
                f.write(f"{platform.upper()}\n")
                f.write(f"URL: {self.platform_urls.get(platform, 'N/A')}\n")
                f.write(f"{'='*60}\n\n")
                f.write(content)
                f.write("\n\n")
        
        files["combined"] = combined_file
        
        logger.info(f"Generated {len(files)} content files in {output_dir}")
        return files
