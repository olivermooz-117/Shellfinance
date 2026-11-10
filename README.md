# ShellFinance

An intelligent global personal finance and investment management platform.

## Technology

- Next.js and TypeScript
- Python and Flask
- PostgreSQL
- SQLAlchemy and Alembic
- Redis
- Ollama for local AI development
- Docker Compose

## Project Structure

- `frontend/` - Next.js application
- `backend/` - Flask API and business logic
- `docs/` - Technical documentation
- `infrastructure/` - Development and deployment infrastructure

## Local Development

### 1. Environment

Copy the example environment:

```bash
cp .env.example .env
```

### 2. Database and Redis

```bash
docker compose up -d postgres redis
```

### 3. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app wsgi run --debug --port 5000
```

### 4. Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Local URLs

- Website: http://localhost:3000
- Backend: http://localhost:5000
- API health: http://localhost:5000/api/health
- Database health: http://localhost:5000/api/health/database

## Development Principles

- Secure-by-default architecture.
- Explicit currency handling.
- Decimal arithmetic for financial values.
- Auditable financial operations.
- Provider-independent integrations.
- Tests for critical financial logic.
- No real investment execution without appropriate authorization and regulated partners.

## Project Status

Phase 1: Foundation and initial interface.
