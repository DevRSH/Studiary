from pydantic import BaseModel, Field, field_validator

class CursoCreateRequest(BaseModel):
    periodo_id: int = Field(..., gt=0, description="ID del periodo académico")
    nombre: str = Field(..., min_length=1, max_length=200)
    codigo: str | None = Field(None, max_length=20)
    color: str = Field("#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    creditos: int = Field(4, ge=1, le=10)
    
    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

class CursoUpdateRequest(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=200)
    codigo: str | None = Field(None, max_length=20)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    creditos: int | None = Field(None, ge=1, le=10)
