from fastapi import FastAPI
from src.api.routes import router
from src.services.schema_service import SchemaService
from src.config.validation import validate_environment
from src.config.logging import setup_logging, get_logger
import os

setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

if not validate_environment():
    logger.critical("Application startup failed due to invalid environment configuration")
    import sys
    sys.exit(1)

app = FastAPI(
    title="LLM-SQL Query System",
    description="A container ready system for cnverting natural language to SQL queries",
    version="1.0.0"
)

app.include_router(router)

schema_service = SchemaService()


@app.on_event("startup")
async def startup_event():
    """
   Connect to database and get schema info on startup.
   Embeddings initialisation is skipped for ease..  
    """
    try:
        logger.info("Application starting...")
        
        await schema_service.get_schema_info()
        logger.info("Db connection successful")
        logger.info("Application startup was complete")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        logger.warning("Continuing without schema embeddings...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
