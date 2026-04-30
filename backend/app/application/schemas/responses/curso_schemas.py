from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CursoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    periodo_id: int
    nombre: str
    codigo: str | None
    color: str
    creditos: int
    created_at: datetime
    updated_at: datetime

class CursoDetailResponse(CursoResponse):
    evaluaciones: list = [] # To be strongly typed once EvaluacionResponse is built
    promedio_actual: float | None = None
