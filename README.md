
cd ~/Shellfinance

cat > README.md <<'EOF'
# ShellFinance

An intelligent personal finance and investment management platform.

ShellFinance aims to bring financial visibility, money management and
investment insights together in one workspace.

> **Project status:** Phase 1 — Foundation.
>
> Authentication, financial features, investment integrations and account
> management are not yet implemented. The dashboard currently displays
> illustrative data, not real account balances.

## Technology stack

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4

### Backend
- Python
- Flask
- Flask-CORS
- Flask-SQLAlchemy
- SQLAlchemy
- PostgreSQL
- Psycopg

### Development infrastructure
- Docker Compose
- PostgreSQL 17
- Redis 7

Alembic and Ollama are planned development dependencies/integrations.
Database migrations and Ollama-backed features have not yet been implemented.

## Project structure

```text
Shellfinance/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── extensions.py
│   ├── tests/
│   │   └── test_health.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── wsgi.py
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── login/
│   │       ├── register/
│   │       ├── globals.css
│   │       ├── layout.tsx
│   │       └── page.tsx
│   └── package.json
├── backups/              # Local only; excluded from Git
├── docker-compose.yml
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- Docker Engine and Docker Compose plugin

## Local development

### 1. Configure environment variables

From the repository root:

```bash
cp .env.example .env
```

Edit `.env` and set a unique development secret and database password.

Do not commit `.env`.

### 2. Start PostgreSQL and Redis

```bash
docker compose up -d postgres redis
```

PostgreSQL is exposed on host port `5434`.

Redis is exposed on host port `6379`.

Check service status:

```bash
docker compose ps
```

### 3. Configure the backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements-dev.txt
```

Run the backend:

```bash
python -m flask --app wsgi run --debug --port 5000
```

The application loads the repository-root `.env` when creating the Flask app.

### 4. Configure the frontend

Open another terminal:

```bash
cd ~/Shellfinance/frontend

npm install
npm run dev
```

### 5. Local URLs

| Service | URL |
|---|---|
| Website | http://localhost:3000 |
| Login placeholder | http://localhost:3000/login |
| Registration placeholder | http://localhost:3000/register |
| Backend | http://localhost:5000 |
| API health | http://localhost:5000/api/health |
| Database health | http://localhost:5000/api/health/database |

## Testing

### Backend

```bash
cd ~/Shellfinance/backend

source .venv/bin/activate
pip install -r requirements-dev.txt

PYTHONPATH="$PWD" python -m pytest -v
```

The health endpoint tests use an isolated in-memory SQLite database.

They do not require a live PostgreSQL container.

### Frontend

```bash
cd ~/Shellfinance/frontend

npm run lint
npm run build
```

## Security principles

ShellFinance is not yet ready to accept real financial information.

Before launching user-facing financial features, the project must implement:

- Secure authentication and account recovery.
- Strong password hashing.
- Session or token lifecycle management.
- Rate limiting and abuse protection.
- Authorization and per-user data isolation.
- Encryption and secure handling of provider tokens.
- Auditable financial operations.
- Secure secrets management.
- Appropriate financial-data retention and deletion policies.

Never request or store users' online banking passwords.

Bank integrations should use appropriate regulated financial-data providers.

## Financial engineering principles

Future financial features should follow these principles:

- Use decimal arithmetic for money, never binary floating-point.
- Store explicit ISO 4217 currency codes.
- Store timestamps in UTC.
- Use immutable financial transaction records and explicit reversals.
- Record exchange-rate sources and timestamps.
- Use database constraints and migrations for data integrity.
- Maintain auditable financial operations.
- Do not present simulated returns as actual performance.
- Do not execute investment transactions without appropriate authorization
  and regulated partners.

## Database migrations

Alembic is included as a dependency, but migrations are not initialized yet.

Before introducing financial models, establish a migration strategy and
review the schema for monetary precision, currency handling, auditability
and data isolation.

## Continuous integration

GitHub Actions runs backend tests and frontend lint/build checks on pushes
and pull requests to the main branch.

## Project status

Current phase: Phase 1 — Foundation and initial interface.
EOF
