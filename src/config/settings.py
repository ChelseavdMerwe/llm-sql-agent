import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Database (REQUIRED)
    postgres_uri: str
    
    # Redis (REQUIRED)
    redis_url: str
    redis_cache_ttl: int
    
    # MLflow (REQUIRED)
    mlflow_tracking_uri: str
    mlflow_experiment_name: str
    
    # AWS Bedrock (REQUIRED)
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    bedrock_inference_profile_id: str
    bedrock_embedding_model: str
    
    # Schema embeddings
    embedding_similarity_threshold: float
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        validate_default = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
