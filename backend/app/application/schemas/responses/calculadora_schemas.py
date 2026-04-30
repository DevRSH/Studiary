from typing import List, Dict
from pydantic import BaseModel

class DistribucionSchema(BaseModel):
    evaluacion: str
    nota_necesaria: float
    ponderacion: float

class EstrategiaResponse(BaseModel):
    nombre: str
    descripcion: str
    distribuciones: List[DistribucionSchema]
    dificultad: str

class ProyeccionResponse(BaseModel):
    curso_id: int
    nota_objetivo: float
    nota_actual: float
    ponderacion_usada: float
    ponderacion_restante: float
    es_factible: bool
    margen_error: float
    estrategias: List[EstrategiaResponse]
