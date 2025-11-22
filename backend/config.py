"""Configuration management for FastFit Radar."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (parent directory)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Application configuration."""
    
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    
    # Redis Agent Memory Server Configuration
    AGENT_MEMORY_SERVER_URL = os.getenv("AGENT_MEMORY_SERVER_URL", "http://localhost:8001")
    AGENT_MEMORY_USER_ID = os.getenv("AGENT_MEMORY_USER_ID", "fastfit_radar")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # RSS Feed Configuration
    RSS_FEEDS = [
        "https://www.adidas-group.com/en/rss/news/",
        "https://hypebeast.com/feed",
        "https://www.luxurydaily.com/rss-feeds/",
        # Add more RSS feeds here
    ]
    
    # Polling Configuration
    RSS_POLLING_INTERVAL_SECONDS = int(os.getenv("RSS_POLLING_INTERVAL_SECONDS", "600"))  # Default 10 minutes
    NOTIFICATION_INTERVAL_SECONDS = int(os.getenv("NOTIFICATION_INTERVAL_SECONDS", "1800"))  # Default 30 minutes
    
    # Vector Index Configuration
    VECTOR_INDEX_NAME = "fashion_posts"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536
    
    # Email Configuration
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "FastFit Radar <onboarding@resend.dev>")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

config = Config()

