import os
from typing import List

class Settings:
    # API Configuration
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = "mistral-ocr-latest"
    
    # File Configuration
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".pptx", ".png", ".jpg", ".jpeg", ".avif"]
    TEMP_DIR: str = "data/temp"
    
    # Security Configuration
    ALLOWED_DOMAINS: List[str] = ["example.com", "trusted-domain.com"]
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 heure
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/mistral_ocr.log"
    
    # Output Configuration
    OUTPUT_FORMAT: str = "json"  # json, csv, xml
    INCLUDE_IMAGES: bool = True
    IMAGE_LIMIT: int = 10
    IMAGE_MIN_SIZE: int = 100

settings = Settings() 