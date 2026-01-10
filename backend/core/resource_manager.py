import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager
from backend.config.enhanced_settings import get_settings

logger = logging.getLogger(__name__)

class ResourceManager:
    """
    Manages global system resources and concurrency limits.
    Distinguishes between 'local' (CPU/GPU heavy) and 'cloud' (IO heavy) workloads.
    """
    _instance: Optional['ResourceManager'] = None
    
    def __init__(self):
        self.settings = get_settings()
        self._local_semaphore: Optional[asyncio.Semaphore] = None
        self._cloud_semaphore: Optional[asyncio.Semaphore] = None
        self._initialized = False

    @classmethod
    def get_instance(cls) -> 'ResourceManager':
        if cls._instance is None:
            cls._instance = ResourceManager()
        return cls._instance

    def initialize(self):
        """Initialize semaphores if not already initialized. Safe to call multiple times."""
        if not self._initialized:
            # We must create semaphores inside an active event loop or lazily.
            # To be safe, we'll create them lazily in the acquire methods if missing, 
            # or rely on the fact that this is called within an async context normally.
            # However, asyncio.Semaphore expects a running loop if not created in one.
            # Best pattern is to check validity on use or explicit async init.
            # Here we just flag it, and create actual objects on first use if loop is running.
            pass
            
    def _ensure_semaphores(self):
        if self._local_semaphore is None:
            limit = self.settings.scheduling.max_local_concurrent_tasks
            self._local_semaphore = asyncio.Semaphore(limit)
            logger.info(f"Initialized Local Resource Semaphore with limit: {limit}")
            
        if self._cloud_semaphore is None:
            limit = self.settings.scheduling.max_cloud_concurrent_tasks
            self._cloud_semaphore = asyncio.Semaphore(limit)
            logger.info(f"Initialized Cloud Resource Semaphore with limit: {limit}")

    @asynccontextmanager
    async def acquire_local(self):
        """Acquire a slot for a local (heavy) resource task."""
        self._ensure_semaphores()
        # pyright: ignore [reportOptionalMemberAccess]
        async with self._local_semaphore:
            yield

    @asynccontextmanager
    async def acquire_cloud(self):
        """Acquire a slot for a cloud (network/IO) resource task."""
        self._ensure_semaphores()
        # pyright: ignore [reportOptionalMemberAccess]
        async with self._cloud_semaphore:
            yield

# Global instance accessor
resource_manager = ResourceManager.get_instance()
