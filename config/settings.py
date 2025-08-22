"""
Configuration settings for the Pipechat + BAML comparison project.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Provider selection: "openai" or "gemini"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    # OpenAI Configuration (optional if using Gemini)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Google Gemini Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # ElevenLabs Configuration (Text-to-Speech) - optional
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # Deepgram Configuration (Speech-to-Text) - optional
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    
    # Pipechat Configuration
    PIPECHAT_LOG_LEVEL: str = os.getenv("PIPECHAT_LOG_LEVEL", "INFO")
    
    # BAML Configuration (optional)
    BAML_API_KEY: str = os.getenv("BAML_API_KEY", "")
    
    # Test Configuration
    TEST_MODE: bool = os.getenv("TEST_MODE", "true").lower() == "true"
    METRICS_SAVE_PATH: str = os.getenv("METRICS_SAVE_PATH", "./metrics/")
    
    # Model Configuration
    DEFAULT_MODEL_OPENAI: str = os.getenv("DEFAULT_MODEL_OPENAI", "gpt-4o-mini")
    DEFAULT_MODEL_GEMINI: str = os.getenv("DEFAULT_MODEL_GEMINI", "gemini-1.5-flash")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    @classmethod
    def get_default_model(cls) -> str:
        if cls.LLM_PROVIDER == "openai":
            return cls.DEFAULT_MODEL_OPENAI
        return cls.DEFAULT_MODEL_GEMINI
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings for chosen provider are present."""
        missing_keys = []
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
        if cls.LLM_PROVIDER == "gemini" and not cls.GOOGLE_API_KEY:
            missing_keys.append("GOOGLE_API_KEY")
        
        if missing_keys:
            print(f"Missing required environment variables: {missing_keys}")
            return False
        return True


# Global settings instance
settings = Settings()
