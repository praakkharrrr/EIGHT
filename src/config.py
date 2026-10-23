import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """Central configuration for EIGHT — AI Crash-Test Lab."""
    
    # Official Gemma 4 and Gemini API model identifiers:
    SUPPORTED_MODELS: tuple = (
        "gemma-4-26b-a4b-it",
        "gemma-4-31b-it",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    )
    
    # Default model: Official Gemma 4
    DEFAULT_MODEL: str = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")
    
    # API configuration
    API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    
    # Request timeouts & limits
    REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("GEMMA_TIMEOUT", "30.0"))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("GEMMA_MAX_TOKENS", "2048"))
    TEMPERATURE: float = float(os.getenv("GEMMA_TEMPERATURE", "0.2"))
    
    # Application settings
    APP_TITLE: str = "EIGHT — AI Crash-Test Lab"
    APP_TAGLINE: str = "Don't trust the answer. Test the intelligence behind it."
    BENCHMARK_FILE_PATH: str = os.path.join(os.path.dirname(__file__), "..", "data", "benchmark_tasks.json")

    @classmethod
    def get_api_key(cls, runtime_override: Optional[str] = None) -> Optional[str]:
        """Returns runtime override if provided, else environment variable."""
        if runtime_override and runtime_override.strip():
            return runtime_override.strip()
        return os.getenv("GEMINI_API_KEY", None)

    @classmethod
    def is_api_configured(cls, runtime_override: Optional[str] = None) -> bool:
        """Checks if a valid-length API key is provided."""
        key = cls.get_api_key(runtime_override)
        return bool(key and len(key.strip()) > 8)
