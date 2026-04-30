"""Application schemas package."""

from app.application.schemas.requests import periodo_requests, curso_requests
from app.application.schemas.responses import periodo_responses, curso_responses

__all__ = [
    "periodo_requests",
    "curso_requests",
    "periodo_responses",
    "curso_responses",
]
