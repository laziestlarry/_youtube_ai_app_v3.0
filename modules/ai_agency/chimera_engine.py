import logging
import os
from typing import Dict, Any, Optional
import httpx
import asyncio
from openai import AsyncOpenAI
from backend.config.enhanced_settings import get_settings

logger = logging.getLogger(__name__)

class ChimeraEngine:
    """
    The 'Chimera Engine' manages multi-model orchestration.
    It can flip between local Ollama models and cloud-based APIs (OpenAI/Gemini/Groq)
    based on task complexity, cost, and availability.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        # Modes: local, cloud, hybrid (local-first with cloud fallback)
        self.default_mode = os.getenv("CHIMERA_DEFAULT_MODE", "hybrid").lower()
        self.fallback_to_cloud = os.getenv("CHIMERA_FALLBACK_TO_CLOUD", "true").lower() in ("1", "true", "yes")
        self._provider_env = os.getenv("AI_PROVIDER")
        self.ai_provider = (self._provider_env or self.settings.ai.provider or "openai").lower()
        self.model_name = (
            os.getenv("OPENAI_MODEL")
            or os.getenv("AI_MODEL_NAME")
            or self.settings.ai.model_name
        )
        self.max_tokens = self._parse_int(os.getenv("AI_MAX_TOKENS"), self.settings.ai.max_tokens)
        self.temperature = self._parse_float(os.getenv("AI_TEMPERATURE"), self.settings.ai.temperature)
        self._openai_client: Optional[AsyncOpenAI] = None
        self._openai_api_key: Optional[str] = None
        self.vertex_project = os.getenv("VERTEXAI_PROJECT") or os.getenv("GCP_PROJECT_ID")
        self.vertex_location = os.getenv("VERTEXAI_LOCATION", "us-central1")
        self.vertex_model = os.getenv("VERTEXAI_MODEL", "gemini-1.5-pro-002")
        self.vertex_fallback = os.getenv("VERTEXAI_FALLBACK_TO_OPENAI", "true").lower() in ("1", "true", "yes")

    @staticmethod
    def _parse_int(value: Optional[str], fallback: int) -> int:
        if value is None:
            return fallback
        try:
            return int(value)
        except ValueError:
            return fallback

    @staticmethod
    def _parse_float(value: Optional[str], fallback: float) -> float:
        if value is None:
            return fallback
        try:
            return float(value)
        except ValueError:
            return fallback

    def _get_openai_client(self) -> AsyncOpenAI:
        api_key = os.getenv("OPENAI_API_KEY") or self.settings.ai.openai_api_key
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        if not self._openai_client or api_key != self._openai_api_key:
            self._openai_client = AsyncOpenAI(api_key=api_key)
            self._openai_api_key = api_key
        return self._openai_client

    async def generate_response(self, prompt: str, task_type: str = "general") -> str:
        """
        Generates a response using the most appropriate model.
        """
        mode = self._determine_mode(task_type)

        if mode == "cloud":
            return await self._call_cloud_api(prompt)

        local_result: Optional[str] = None
        if mode in ("local", "hybrid"):
            local_result = await self._call_ollama(prompt)
            if not self._should_fallback(local_result):
                return local_result

        # Fallback to cloud when local processing fails or hybrid mode requires it
        return await self._call_cloud_api(prompt)

    def _determine_mode(self, task_type: str) -> str:
        """Determines whether to use local or cloud based on task."""
        # Simple tasks or recurring maintenance can use local Ollama
        local_tasks = ["status_check", "log_analysis", "minor_refactor"]
        if task_type in local_tasks:
            return "local"
        valid_modes = {"local", "cloud", "hybrid"}
        return self.default_mode if self.default_mode in valid_modes else "cloud"

    def _should_fallback(self, local_response: Optional[str]) -> bool:
        """Decide whether to fall back to cloud after a local attempt."""
        if not self.fallback_to_cloud:
            return False
        if not local_response:
            return True

        lowered = str(local_response).lower()
        error_signals = [
            "ollama error",
            "ollama connection failed",
            "failed to connect",
            "no response from ollama",
        ]
        return any(signal in lowered for signal in error_signals)

    async def _call_ollama(self, prompt: str) -> str:
        """Calls the local Ollama instance with resource limiting."""
        from backend.core.resource_manager import resource_manager
        
        async with resource_manager.acquire_local():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.ollama_url,
                        json={
                            "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=120.0  # Increased timeout for local processing
                    )
                    if response.status_code == 200:
                        return response.json().get("response", "No response from Ollama")
                    return f"Ollama Error: {response.status_code}"
            except Exception as e:
                import traceback
                error_msg = str(e) or type(e).__name__
                logger.error(f"Ollama call failed [{type(e).__name__}]: {error_msg}")
                # Optional: debug traceback for intermittent connection issues
                # logger.debug(traceback.format_exc())
                return f"Ollama Connection Failed: {error_msg}"

    async def _call_cloud_api(self, prompt: str) -> str:
        """Calls the configured cloud AI with resource limiting."""
        from backend.core.resource_manager import resource_manager

        async with resource_manager.acquire_cloud():
            provider = self.ai_provider
            if provider in ("vertexai", "vertex", "gemini"):
                try:
                    return await self._call_vertex_ai(prompt)
                except Exception as exc:
                    logger.warning("Vertex AI call failed: %s", exc)
                    if self.vertex_fallback:
                        provider = "openai"
                    else:
                        raise
            if provider not in ("openai", "cloud"):
                api_key = os.getenv("OPENAI_API_KEY") or self.settings.ai.openai_api_key
                if not self._provider_env and api_key:
                    logger.warning("AI_PROVIDER '%s' is not supported; defaulting to OpenAI.", provider)
                    provider = "openai"
                else:
                    raise RuntimeError(f"Unsupported AI provider: {provider}")

            client = self._get_openai_client()
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise assistant. Follow the user's instructions and return only the requested output.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            content = response.choices[0].message.content
            return content or ""

    async def _call_vertex_ai(self, prompt: str) -> str:
        """Calls Vertex AI (Gemini) via REST API."""
        from google.auth import default
        from google.auth.transport.requests import Request

        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        credentials, project = default(scopes=scopes)
        credentials.refresh(Request())

        project_id = self.vertex_project or project
        if not project_id:
            raise RuntimeError("VERTEXAI_PROJECT or GCP_PROJECT_ID is required for Vertex AI.")

        endpoint = (
            f"https://{self.vertex_location}-aiplatform.googleapis.com/v1/projects/"
            f"{project_id}/locations/{self.vertex_location}/publishers/google/models/"
            f"{self.vertex_model}:generateContent"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": self.max_tokens,
                "temperature": self.temperature,
            },
        }
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return ""
        return str(parts[0].get("text") or "").strip()

chimera_engine = ChimeraEngine()
