"""
Configuration validation utilities
"""
import sys
from src.config.settings import get_settings
from src.config.logging import get_logger

logger = get_logger(__name__)


def validate_environment():
    """
    Validate that all required environment variables are set.
    it exits with error code 1 if the validation fails.
    """
    try:
        settings = get_settings()
        
        # Validate AWS credentials are not placeholder values
        if settings.aws_access_key_id == "your_aws_access_key_here":
            raise ValueError("AWS_ACCESS_KEY_ID is not set to a real value")
        
        if settings.aws_secret_access_key == "your_aws_secret_key_here":
            raise ValueError("AWS_SECRET_ACCESS_KEY is not set to a real value")
        
        # Validate that URLs are properly formatted
        if not settings.postgres_uri.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("POSTGRES_URI must start with postgresql:// or postgresql+asyncpg://")
        
        if not settings.redis_url.startswith("redis://"):
            raise ValueError("REDIS_URL must start with redis://")
        
        if not settings.mlflow_tracking_uri.startswith(("http://", "https://")):
            raise ValueError("MLFLOW_TRACKING_URI must start with http:// or https://")
        
        logger.info("All environment variables validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        logger.error("Please check your .env file and ensure all required variables are set")
        return False


if __name__ == "__main__":
    if not validate_environment():
        sys.exit(1)
