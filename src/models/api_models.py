from pydantic import BaseModel
from typing import Dict, List, Optional


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    sql_query: str
    results: List[Dict]
    relevant_schema: str
    confidence_score: float
    mlflow_run_id: str


class HealthResponse(BaseModel):
    status: str
    redis: bool
    database: Optional[str] = None
