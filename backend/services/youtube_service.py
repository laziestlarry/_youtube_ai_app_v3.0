"""
YouTube API Integration Service
Handles OAuth2 flow and data synchronization with database.
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.core.config import settings
from backend.models.youtube import ChannelStats, VideoAnalytics
from backend.models.user import User

logger = logging.getLogger(__name__)

# Scopes required for the application
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

class YouTubeService:
    """Production YouTube API service with OAuth2 support."""
    
    def __init__(self):
        # Determine redirect URI based on environment
        self.redirect_uri = "http://localhost:8000/oauth/callback"  # Unified platform callback
        
        # Client config for OAuth flow
        self.client_config = {
            "web": {
                "client_id": settings.youtube_client_id,
                "client_secret": settings.youtube_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
    
    def get_login_url(self) -> str:
        """Generate the Google login URL for authorization."""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=SCOPES,
                redirect_uri=self.redirect_uri
            )
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'  # Force consent to get refresh token
            )
            return authorization_url
        except Exception as e:
            logger.error(f"Error generating login URL: {e}")
            raise

    async def exchange_code_for_token(self, code: str, user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Exchange auth code for credentials and save to user."""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=SCOPES,
                redirect_uri=self.redirect_uri
            )
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Store credentials in User model
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if user:
                user.youtube_access_token = credentials.token
                user.youtube_refresh_token = credentials.refresh_token
                user.youtube_token_expiry = credentials.expiry
                await db.commit()
            
            # Initial sync of channel data
            await self.sync_channel_stats(credentials, user_id, db)
            
            return {"status": "success", "message": "YouTube connected successfully"}
            
        except Exception as e:
            logger.error(f"Error exchanging code: {e}")
            raise

    async def sync_channel_stats(self, credentials: Credentials, user_id: int, db: AsyncSession):
        """Fetch and store basic channel statistics."""
        try:
            service = build('youtube', 'v3', credentials=credentials)
            
            # Get my channel
            response = service.channels().list(
                part='snippet,statistics,contentDetails',
                mine=True
            ).execute()
            
            if not response.get('items'):
                logger.warning("No channel found for authenticated user")
                return

            channel = response['items'][0]
            channel_id = channel['id']
            stats = channel['statistics']
            
            # Create or update stats record
            # Check if exists
            result = await db.execute(select(ChannelStats).where(ChannelStats.channel_id == channel_id))
            existing_stats = result.scalars().first()
            
            if existing_stats:
                existing_stats.subscribers = int(stats.get('subscriberCount', 0))
                existing_stats.views = int(stats.get('viewCount', 0))
                existing_stats.video_count = int(stats.get('videoCount', 0))
                existing_stats.fetched_at = datetime.now()
            else:
                new_stats = ChannelStats(
                    channel_id=channel_id,
                    user_id=user_id,
                    subscribers=int(stats.get('subscriberCount', 0)),
                    views=int(stats.get('viewCount', 0)),
                    video_count=int(stats.get('videoCount', 0)),
                )
                db.add(new_stats)
            
            await db.commit()
            
            # Trigger video sync in background (simplified here)
            uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
            await self.sync_recent_videos(service, uploads_playlist_id, channel_id, user_id, db)
            
        except Exception as e:
            logger.error(f"Error syncing channel stats: {e}")
            # Don't raise, just log error for background job
            
    async def sync_recent_videos(self, service, playlist_id: str, channel_id: str, user_id: int, db: AsyncSession):
        """Sync recent videos from the channel."""
        try:
            # Get recent videos from uploads playlist
            response = service.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=10
            ).execute()
            
            for item in response.get('items', []):
                video_id = item['contentDetails']['videoId']
                title = item['snippet']['title']
                upload_date_str = item['snippet']['publishedAt']
                upload_date = datetime.fromisoformat(upload_date_str.replace('Z', '+00:00'))
                
                # Get video stats
                video_response = service.videos().list(
                    part='statistics',
                    id=video_id
                ).execute()
                
                if not video_response.get('items'):
                    continue
                    
                stats = video_response['items'][0]['statistics']
                
                # Create or update video record
                result = await db.execute(select(VideoAnalytics).where(VideoAnalytics.video_id == video_id))
                existing_video = result.scalars().first()
                
                if existing_video:
                    existing_video.views = int(stats.get('viewCount', 0))
                    existing_video.likes = int(stats.get('likeCount', 0))
                    existing_video.comments = int(stats.get('commentCount', 0))
                    existing_video.fetched_at = datetime.now()
                else:
                    new_video = VideoAnalytics(
                        video_id=video_id,
                        channel_id=channel_id,
                        user_id=user_id,
                        title=title,
                        views=int(stats.get('viewCount', 0)),
                        likes=int(stats.get('likeCount', 0)),
                        comments=int(stats.get('commentCount', 0)),
                        upload_date=upload_date
                    )
                    db.add(new_video)
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error syncing videos: {e}")