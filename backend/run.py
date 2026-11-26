"""
Uvicorn Runner Script for AI Accessibility Assistant Backend
"""
import sys
import uvicorn
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

