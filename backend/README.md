# Studiary Backend

Backend API for Studiary - Academic Command Center.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc
