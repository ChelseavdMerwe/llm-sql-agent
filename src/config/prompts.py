class PromptTemplates:
    
    SQL_GENERATION_TEMPLATE = """You are an expert SQL query generator. Given a database schema and question, generate ONLY a SQL query.

IMPORTANT: Return ONLY the SQL query. Do not include any explanations, reasoning, markdown formatting, or additional text.

Database Schema:
{schema}

Question: {question}

Return only the SQL query:"""

    SCHEMA_SEMANTIC_DESCRIPTION_TEMPLATE = """Describe what this database table is used for based on its name and columns:

Table: {table_name}
Columns: {columns}

This table stores:"""

    @classmethod
    def get_sql_prompt(cls, schema: str, question: str) -> str:
        return cls.SQL_GENERATION_TEMPLATE.format(
            schema=schema,
            question=question
        )
    
    @classmethod
    def get_semantic_description_prompt(cls, table_name: str, columns: str) -> str:
        return cls.SCHEMA_SEMANTIC_DESCRIPTION_TEMPLATE.format(
            table_name=table_name,
            columns=columns
        )
