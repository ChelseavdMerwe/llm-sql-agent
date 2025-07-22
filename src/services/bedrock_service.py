import json
from typing import List
import boto3
import numpy as np
from src.config.settings import get_settings
from src.models.database_models import EmbeddingResult


class BedrockService:
    def __init__(self):
        self.settings = get_settings()
        self.client = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key,
            region_name=self.settings.aws_region,
        )
    
    async def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate text using Bedrock claude with the 'Messages API' (its required for Claude 4)
        *Note:  Can change token limit as needed - reduce if you want shorter responses and faster response time
        """
        response = self.client.invoke_model(
            modelId=self.settings.bedrock_inference_profile_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0,
                "top_p": 0.7,
            }),
            accept="application/json",
            contentType="application/json",
        )
        result = json.loads(response["body"].read())
        raw_text = result["content"][0]["text"].strip()
        
        # Clean up the raw text to get only the SQL query
        cleaned_text = raw_text
        
        if "```sql" in cleaned_text:
            start = cleaned_text.find("```sql") + 6
            end = cleaned_text.find("```", start)
            if end != -1:
                cleaned_text = cleaned_text[start:end].strip()
        elif "```" in cleaned_text:
            start = cleaned_text.find("```") + 3
            end = cleaned_text.find("```", start)
            if end != -1:
                cleaned_text = cleaned_text[start:end].strip()
        
        lines = cleaned_text.split('\n')
        sql_lines = []
        found_sql = False
        
        for line in lines:
            line = line.strip()
            if any(line.upper().startswith(keyword) for keyword in ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']):
                found_sql = True
            if found_sql:
                sql_lines.append(line)
        
        if sql_lines:
            cleaned_text = '\n'.join(sql_lines)
        
        return cleaned_text
    
    async def get_embedding(self, text: str) -> EmbeddingResult:
        """
        
        Get the embedding from Bedrock
        
        """
        response = self.client.invoke_model(
            modelId=self.settings.bedrock_embedding_model,
            body=json.dumps({"inputText": text}),
            accept="application/json",
            contentType="application/json",
        )
        result = json.loads(response["body"].read())
        
        return EmbeddingResult(
            embedding=result["embedding"],
            text=text,
            confidence=1.0 
        )
    
    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        """
        Calculate cosine similarity between the two embeddings
        """
        a_np = np.array(a)
        b_np = np.array(b)
        return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))
