# LLM-SQL Query System

A container ready system for converting natural language questions into sql queries using AWS Bedrock, with schema understanding/interpretation
## Architecture

```
src/
├── models/          # Data models (API & database)
├── services/        # Business logic (Bedrock, Cache, Schema, MLflow)
├── api/            # Routes and endpoints
└── config/         # Settings and prompt templates
```

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual credentials
# NOTE: Never commit .env to gh!
```

### 2. Required Env variables

```bash
# AWS Credentials (ARE REQUIRED)
AWS_ACCESS_KEY_ID=your_actual_key
AWS_SECRET_ACCESS_KEY=your_actual_secret
AWS_REGION=region
AWS_BEDROCK_INFERENCE_PROFILE_ID=your_inference_profile_id

# Database (REQUIRED)
POSTGRES_URI=postgresql+asyncpg://user:password@host:5432/database

# OptionalsServices (have defaults)
REDIS_URL=redis://localhost:6379/0
MLFLOW_TRACKING_URI=http://localhost:5000
```

### 3. Run with Docker Compose

```bash
# Starts all the services (Redis, MLflow, API)
docker-compose up --build

# API available at: http://localhost:8001
# MLflow UI at: http://localhost:5000
```

## API Endpoints

### NL query example
```bash
curl -X POST "http://localhost:8001/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What countries recovered fastest from the 2008 financial crisis?"}'
```

### Database Schema info
```bash
curl "http://localhost:8001/schema"
```

### Health check
```bash
curl "http://localhost:8001/health"
```

## Features

- **AWS Bedrock Integration**: Uses an aws model atm for SQL generation
- **Schema Understanding**: Contextual table and column selection
- ** Caching**: Redis for improved performance and logging
- **Experiment Tracking**: MLflow for monitoring and optimization
- **Health Monitoring**: Health checks via api call
- **Error Handling**: Included
- **Type Safety**: Pydantic models with validation
- **Containerized**: Docker Compose for easy deployment

## Deployment:

### Prerequisites
- Docker 
- AWS Bedrock access with model permissions
- PostgreSQL database (existing or new)
- (optional) Redis instance
- (Optional) MLflow tracking server

### Deployment Steps

1. **Environment configuration**
```bash
# Use proper secrets management
cp .env.example .env
```

2. **Infrastructure setup**
```bash
# Deploy with configured settings
docker-compose -f docker-compose.prod.yml up -d
```

### Future: 

3. **Monitoring and logging**
- Set up log aggregation (CloudWatch)
- Configure monitoring (?)
- Set up alerts for health check failures

4. **Security:**
- Use AWS Secrets Manager or similar
- Configure VPC and security groups
- Enable SSL/TLS for all endpoints
- Implement rate limiting

### Production features to consider

- **Scalability**: Use load balancers and multiple instances
- **High Availability**: Deploy across multiple availability zones
- **Backup Strategy**: Regular database backups and disaster recovery
- **Cost Optimization**: Monitor AWS Bedrock usage and implement caching strategies


## Contributing - ToDo:

1. Never commit `.env` files
2. Add tests for new features
3. Follow type hints
4. Update documentation
