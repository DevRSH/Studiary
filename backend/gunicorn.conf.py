"""Gunicorn configuration for production."""
import multiprocessing
import os

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Workers
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # Max 4 en Railway free
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Timeout
timeout = 120
keepalive = 5

# Graceful timeout
graceful_timeout = 30

# Max requests per worker (restart para evitar memory leaks)
max_requests = 1000
max_requests_jitter = 100
