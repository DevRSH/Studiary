"""Integration tests for Periodo API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestPeriodosAPI:
    """Integration tests for /api/v1/periodos."""

    async def test_health_check(self, client: AsyncClient) -> None:
        """GET /health should return 200 with status=healthy."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_list_periodos_empty(self, client: AsyncClient) -> None:
        """GET /api/v1/periodos/ should return empty list initially."""
        response = await client.get("/api/v1/periodos/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_create_periodo(self, client: AsyncClient) -> None:
        """POST /api/v1/periodos/ should create and return a periodo."""
        payload = {
            "nombre": "Semestre 2026-I",
            "fecha_inicio": "2026-01-15",
            "fecha_fin": "2026-06-15",
            "activo": True,
        }
        response = await client.post("/api/v1/periodos/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Semestre 2026-I"
        assert data["id"] is not None
        assert data["activo"] is True

    async def test_create_periodo_invalid_dates(self, client: AsyncClient) -> None:
        """POST with fecha_fin <= fecha_inicio should return 422."""
        payload = {
            "nombre": "Invalido",
            "fecha_inicio": "2026-06-15",
            "fecha_fin": "2026-01-15",
            "activo": True,
        }
        response = await client.post("/api/v1/periodos/", json=payload)
        assert response.status_code == 422

    async def test_get_periodo_not_found(self, client: AsyncClient) -> None:
        """GET /api/v1/periodos/9999 should return 404."""
        response = await client.get("/api/v1/periodos/9999")
        assert response.status_code == 404
