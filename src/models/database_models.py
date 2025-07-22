from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class SchemaTable:
    name: str
    columns: Dict[str, str]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, Any]]
    description: str
    semantic_description: str


@dataclass
class EmbeddingResult:
    embedding: List[float]
    text: str
    confidence: float


@dataclass
class QueryResult:
    rows: List[Dict[str, Any]]
    execution_time: float
    row_count: int
