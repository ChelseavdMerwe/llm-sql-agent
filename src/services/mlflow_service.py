import mlflow
from src.config.settings import get_settings
from src.config.logging import get_logger

logger = get_logger(__name__)


class MLFlowService:
    def __init__(self):
        self.settings = get_settings()
        self.mlflow_available = False
        
        try:
            mlflow.set_tracking_uri(self.settings.mlflow_tracking_uri)
            # Test connection: 
            mlflow.get_tracking_uri()
            mlflow.set_experiment(self.settings.mlflow_experiment_name)
            self.mlflow_available = True
            logger.info("MLflow connection was successful")
        except Exception as e:
            logger.warning(f"MLflow is not available: {e}")
            logger.warning("Continuing without MLflow logging...")
            self.mlflow_available = False
    
    def start_run(self):
        """
        Start a new MLflow run:
        
        """
        if self.mlflow_available:
            return mlflow.start_run()
        else:
            # Return a mock context manager
            return MockMLflowRun()
    
    def log_query_params(self, question: str, relevant_schema: str, generated_sql: str):
        """
        Log the diff query parameters:
        
        """
        if self.mlflow_available:
            mlflow.log_param("question", question)
            mlflow.log_param("relevant_schema", relevant_schema)
            mlflow.log_param("generated_sql", generated_sql)
    
    def log_query_metrics(self, schema_confidence: float, row_count: int, execution_time: float):
        """
        Log the query metrics
        
        """
        if self.mlflow_available:
            mlflow.log_metric("schema_confidence", schema_confidence)
            mlflow.log_metric("row_count", row_count)
            mlflow.log_metric("execution_time", execution_time)
    
    def log_error(self, error: str):
        """
        Log error information:
        
        """
        if self.mlflow_available:
            mlflow.log_param("error", error)


class MockMLflowRun:
    """
    Mock the MLflow run for when MLflow is not available:
    
    """
    def __init__(self):
        self.info = MockRunInfo()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockRunInfo:
    """
    Mock the run info
    
    """
    def __init__(self):
        self.run_id = "mock-run-id"
