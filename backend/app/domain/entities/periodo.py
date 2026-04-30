"""Domain entity: Periodo Académico.

Entidad pura sin dependencias de infraestructura.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class PeriodoEntity:
    """Representa un periodo académico (semestre, trimestre, etc.).

    Attributes:
        id: Identificador único.
        nombre: Nombre descriptivo (e.g., "Semestre 2026-I").
        fecha_inicio: Fecha de inicio del periodo.
        fecha_fin: Fecha de fin del periodo.
        activo: Indica si este es el periodo actual.
    """

    nombre: str
    fecha_inicio: date
    fecha_fin: date
    activo: bool = True
    id: int | None = None

    def __post_init__(self) -> None:
        """Validate business invariants."""
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        if not self.nombre.strip():
            raise ValueError("nombre no puede estar vacío")
