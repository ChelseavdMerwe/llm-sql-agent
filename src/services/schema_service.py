from typing import Dict, List, Tuple
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config.settings import get_settings
from src.models.database_models import SchemaTable, QueryResult
from src.services.bedrock_service import BedrockService
from src.config.prompts import PromptTemplates
from src.config.logging import get_logger

logger = get_logger(__name__)


class SchemaService:
    def __init__(self):
        
        self.settings = get_settings()
        self.bedrock_service = BedrockService()
        self.embeddings_cache: Dict[str, List[float]] = {}
        self.schema_details: Dict[str, SchemaTable] = {}
        

        self.async_engine = create_async_engine(self.settings.postgres_uri, echo=False)
        self.async_session = sessionmaker(self.async_engine, class_=AsyncSession, expire_on_commit=False)
    
    async def initialize_schema_embeddings(self) -> None:
        """
        Initialise and cache the schema embeddings
        
        """
        sync_engine = create_engine(self.settings.postgres_uri.replace("+asyncpg", ""))
        inspector = inspect(sync_engine)
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            pks = inspector.get_pk_constraint(table_name)['constrained_columns']
            fks = inspector.get_foreign_keys(table_name)
            
            # Create a description
            technical_desc = f"Table '{table_name}' with columns: "
            technical_desc += ", ".join([f"{col['name']} ({col['type']})" for col in columns])
            
            # Generate a semantic description using the LLM:
            columns_str = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
            semantic_prompt = PromptTemplates.get_semantic_description_prompt(table_name, columns_str)
            semantic_desc = await self.bedrock_service.generate_text(semantic_prompt, max_tokens=100)
            
            schema_table = SchemaTable(
                name=table_name,
                columns={col['name']: str(col['type']) for col in columns},
                primary_keys=pks,
                foreign_keys=fks,
                description=technical_desc,
                semantic_description=semantic_desc
            )
            self.schema_details[table_name] = schema_table
            
            tech_embedding = await self.bedrock_service.get_embedding(technical_desc)
            sem_embedding = await self.bedrock_service.get_embedding(semantic_desc)
            
            self.embeddings_cache[f"{table_name}_technical"] = tech_embedding.embedding
            self.embeddings_cache[f"{table_name}_semantic"] = sem_embedding.embedding
    
    async def find_relevant_schema(self, question: str) -> Tuple[str, float]:
        """
        Find the most relevant schema parts for a question
        
        """
        if not self.embeddings_cache:
            logger.info("Embeddings are not initialized, returning all schema info")
            await self.get_schema_info()
            schema_text = "Available tables:\n"
            for table_name, table_info in self.schema_details.items():
                schema_text += f"\n{table_info.description}"
            return schema_text, 0.5 
        
        question_embedding = await self.bedrock_service.get_embedding(question)
        
        best_score = -1
        relevant_tables = []
        
        for table_name in self.schema_details:
            # cosine similarity scores
            technical_score = self.bedrock_service.cosine_similarity(
                question_embedding.embedding,
                self.embeddings_cache[f"{table_name}_technical"]
            )
            semantic_score = self.bedrock_service.cosine_similarity(
                question_embedding.embedding,
                self.embeddings_cache[f"{table_name}_semantic"]
            )
            
            # weighted combinations
            combined_score = (technical_score + 2 * semantic_score) / 3
            
            if combined_score > self.settings.embedding_similarity_threshold:
                relevant_tables.append((table_name, combined_score))
                if combined_score > best_score:
                    best_score = combined_score
        
        relevant_tables.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_tables:
            schema_text = "Relevant tables:\\n"
            for table_name, score in relevant_tables[:3]: 
                table_info = self.schema_details[table_name]
                schema_text += f"\\n{table_info.description}"
                
                # Add fk relationships
                for fk in table_info.foreign_keys:
                    if any(fk['referred_table'] == t[0] for t in relevant_tables):
                        schema_text += f"\\nRelated to {fk['referred_table']} via {fk['constrained_columns']}"
            
            return schema_text, best_score
        
        return "No relevant schema found", 0.0
    
    async def execute_query(self, sql: str) -> QueryResult:
        """
        Execute the sql query and return the results
        
        """
        import time
        start_time = time.time()
        
        async with self.async_session() as session:
            result = await session.execute(text(sql))
            
            raw_rows = result.fetchall()
            rows = []
            if raw_rows:
                
                columns = list(result.keys())
                for row in raw_rows:
                    
                    row_dict = {}
                    for i, column in enumerate(columns):
                        row_dict[column] = row[i]
                    rows.append(row_dict)
            await session.commit()
        
        execution_time = time.time() - start_time
        
        return QueryResult(
            rows=rows,
            execution_time=execution_time,
            row_count=len(rows)
        )
    
    async def get_schema_info(self) -> Dict[str, SchemaTable]:
        """
        Get schema information without embeddings (for API endpoint)
        (this is used when embeddings are not initialised.)
        """
        if not self.schema_details:
        
            sync_engine = create_engine(self.settings.postgres_uri.replace("+asyncpg", ""))
            inspector = inspect(sync_engine)
            
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                pks = inspector.get_pk_constraint(table_name)['constrained_columns']
                fks = inspector.get_foreign_keys(table_name)
                
                description = f"Table '{table_name}' with columns: "
                description += ", ".join([f"{col['name']} ({col['type']})" for col in columns])
                
                schema_table = SchemaTable(
                    name=table_name,
                    columns={col['name']: str(col['type']) for col in columns},
                    primary_keys=pks,
                    foreign_keys=fks,
                    description=description,
                    semantic_description=""
                )
                self.schema_details[table_name] = schema_table
        
        return self.schema_details
