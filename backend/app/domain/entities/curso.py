"""Domain entity: Curso.

Entidad pura sin dependencias de infraestructura.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CursoEntity:
    """Representa un curso o materia dentro de un periodo académico.

    Attributes:
        id: Identificador único.
        nombre: Nombre del curso (e.g., "Cálculo Diferencial").
        codigo: Código oficial del curso (e.g., "MAT-101").
        creditos: Número de créditos académicos.
        periodo_id: FK al periodo académico al que pertenece.
        color: Color HEX para identificación visual en el UI.
        docente: Nombre del docente responsable (opcional).
    """

    nombre: str
    creditos: int
    periodo_id: int
    codigo: str = ""
    color: str = "#6366f1"
    docente: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        """Validate business invariants."""
        if self.creditos <= 0:
            raise ValueError("creditos debe ser mayor a 0")
        if not self.nombre.strip():
            raise ValueError("nombre no puede estar vacío")
