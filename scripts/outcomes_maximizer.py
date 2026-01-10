import os
import requests
import logging
from datetime import datetime
from pathlib import Path

# Try to load .env manually if python-dotenv isn't guaranteed
def load_env_manual():
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outcomes_maximizer")

def check_env():
    logger.info("🔍 Checking environment variables...")
    required = [
        "DATABASE_URL", "GEMINI_API_KEY", "SHOPIER_PERSONAL_ACCESS_TOKEN", 
        "BIGQUERY_PROJECT", "STORAGE_GCS_BUCKET"
    ]
    missing = [r for r in required if not os.environ.get(r)]
    if missing:
        logger.error(f"❌ Missing critical keys: {missing}")
        return False
    logger.info("✅ All critical keys detected.")
    return True

def check_branding():
    logger.info("🏷️ Checking project branding...")
    project_id = os.environ.get("BIGQUERY_PROJECT")
    if project_id != "propulse-autonomax":
        logger.warning(f"⚠️ Project ID mismatch: Found '{project_id}', expected 'propulse-autonomax'")
    else:
        logger.info("✅ Branding aligned: propulse-autonomax")

def check_system_pulse():
    logger.info("💓 Pulsing system health...")
    try:
        # Assuming backend is running locally for this check
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ System Pulse: {response.json().get('status')}")
        else:
            logger.error(f"❌ System Pulse failed with status: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ Could not reach local backend: {e}")

def run_maximizer():
    print("\n--- 🚀 OUTCOMES MAXIMIZER: LAUNCH READINESS ---")
    load_env_manual()
    check_env()
    check_branding()
    check_system_pulse()
    print("--- 🏁 MAXIMIZER COMPLETE --- \n")

if __name__ == "__main__":
    run_maximizer()
