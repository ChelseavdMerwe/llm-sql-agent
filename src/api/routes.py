import asyncio
from fastapi import APIRouter, HTTPException, Depends
from src.models.api_models import QueryRequest, QueryResponse, HealthResponse
from src.services.cache_service import CacheService
from src.services.schema_service import SchemaService
from src.services.bedrock_service import BedrockService
from src.services.mlflow_service import MLFlowService
from src.config.prompts import PromptTemplates

router = APIRouter()

# Services:
cache_service = CacheService()
schema_service = SchemaService()
bedrock_service = BedrockService()
mlflow_service = MLFlowService()


@router.post("/query", response_model=QueryResponse)
async def query_sql(request: QueryRequest):
    
    """
    
    This endpoint processes a natural language question, it then generates a SQL query using a LLM and then
    executes it against the database and returns the results with relevant schema information.
    """
    with mlflow_service.start_run() as run:
        try:
            
            cached_result = await cache_service.get_cached_query(request.question)
            if cached_result:
                return cached_result
            
            relevant_schema, confidence = await schema_service.find_relevant_schema(request.question)
            
            sql_prompt = PromptTemplates.get_sql_prompt(relevant_schema, request.question)
            sql = await bedrock_service.generate_text(sql_prompt)
            
            query_result = await schema_service.execute_query(sql)
            
            response = QueryResponse(
                question=request.question,
                sql_query=sql,
                results=query_result.rows,
                relevant_schema=relevant_schema,
                confidence_score=confidence,
                mlflow_run_id=run.info.run_id
            )
            
            await cache_service.cache_query_result(request.question, response)
            
            mlflow_service.log_query_params(request.question, relevant_schema, sql)
            mlflow_service.log_query_metrics(confidence, query_result.row_count, query_result.execution_time)
            
            return response
            
        except Exception as e:
            mlflow_service.log_error(str(e))
            raise HTTPException(status_code=500, detail=f"Query failed: {e}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
   This endpoint checks the health of the service.
   It returns a status indicating whether the service is healthy or not.
    
    """
    try:
        redis_status = await cache_service.ping()
        return HealthResponse(
            status="healthy" if redis_status else "degraded",
            redis=redis_status
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")


@router.post("/schema/refresh")
async def refresh_schema():
    """

    This endpoint re-initialises/refreshes the schema embeddings used for generating SQL queries.
    
    """
    try:
        await schema_service.initialize_schema_embeddings()
        return {"message": "Schema embeddings refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema refresh failed: {e}")


@router.get("/schema")
async def get_schema():
    """
    
    This endpoint get's the database schema info.
    
    """
    try:
        schema_info = await schema_service.get_schema_info()
        return {
            "tables": [
                {
                    "name": table.name,
                    "columns": table.columns,
                    "primary_keys": table.primary_keys,
                    "description": table.description
                }
                for table in schema_info.values()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema retrieval failed: {e}")
