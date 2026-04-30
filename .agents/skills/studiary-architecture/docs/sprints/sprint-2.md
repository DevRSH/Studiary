
---

# 🚀 SPRINT 2: MOTOR DE CÁLCULO PREDICTIVO DE NOTAS

## 1. OBJETIVO DE EJECUCIÓN
Implementar el motor matemático de proyección de notas que calcula el promedio ponderado actual de un curso, proyecta las notas necesarias en evaluaciones pendientes para alcanzar un objetivo académico, genera múltiples estrategias de distribución de esfuerzo y proporciona análisis de factibilidad. Este sprint incluye la exposición de endpoints especializados y un componente frontend interactivo.

## 2. ENTREGABLES ESPERADOS
*   **CalculadoraService**: Lógica matemática de proyección (DTOs no persistidos).
*   **Algoritmos de Distribución**: Estrategias Uniforme y Realista con margen.
*   **API RESTful**: Endpoints `/api/v1/calculadora/proyeccion/{curso_id}` y `/promedio/{curso_id}`.
*   **Schemas Pydantic**: `ProyeccionResponse` y `EstrategiaResponse`.
*   **Frontend UI**: Componente `CalculadoraNotas` con slider interactivo y visualización *color-coded*.
*   **Testing**: Cobertura >80% en lógica de proyección.

---

## 3. IMPLEMENTACIÓN BACKEND

### Tarea 3.1: DTOs y Lógica del Motor (`calculadora_service.py`)
```python
from typing import List, Dict, Optional
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.models.curso import Curso
from app.infrastructure.models.evaluacion import Evaluacion, EstadoEvaluacion
from app.core.exceptions import NotFoundException, ValidationException

@dataclass
class EstrategiaDistribucion:
    nombre: str
    descripcion: str
    distribuciones: List[Dict]
    dificultad: str

@dataclass
class ProyeccionNotas:
    curso_id: int
    nota_objetivo: float
    nota_actual: float
    ponderacion_usada: float
    ponderacion_restante: float
    es_factible: bool
    margen_error: float
    estrategias: List[EstrategiaDistribucion]

class CalculadoraService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def calcular_proyeccion(self, curso_id: int, nota_objetivo: float) -> ProyeccionNotas:
        if not (1.0 <= nota_objetivo <= 7.0):
            raise ValidationException(f"Nota objetivo {nota_objetivo} fuera de rango [1.0, 7.0]")

        result = await self.db.execute(
            select(Curso).where(Curso.id == curso_id).options(selectinload(Curso.evaluaciones))
        )
        curso = result.scalar_one_or_none()
        
        if not curso: raise NotFoundException(f"Curso {curso_id} no encontrado")
        if not curso.evaluaciones: raise ValidationException(f"Curso '{curso.nombre}' sin evaluaciones")

        rendidas = [e for e in curso.evaluaciones if e.estado == EstadoEvaluacion.CORREGIDA and e.nota_obtenida is not None]
        pendientes = [e for e in curso.evaluaciones if e.estado == EstadoEvaluacion.PENDIENTE]

        suma_ponderada = sum(e.nota_obtenida * e.ponderacion_porcentaje for e in rendidas)
        pond_usada = sum(e.ponderacion_porcentaje for e in rendidas)
        pond_restante = sum(e.ponderacion_porcentaje for e in pendientes)
        
        nota_actual = suma_ponderada / pond_usada if pond_usada > 0 else 0.0

        if not pendientes:
            return ProyeccionNotas(curso_id, nota_objetivo, nota_actual, pond_usada, 0.0, nota_actual >= nota_objetivo, 0.0, [])

        nota_promedio_necesaria = ((nota_objetivo * 100) - suma_ponderada) / pond_restante
        estrategias = self._generar_estrategias(pendientes, nota_promedio_necesaria)

        return ProyeccionNotas(
            curso_id=curso_id,
            nota_objetivo=nota_objetivo,
            nota_actual=nota_actual,
            ponderacion_usada=pond_usada,
            ponderacion_restante=pond_restante,
            es_factible=1.0 <= nota_promedio_necesaria <= 7.0,
            margen_error=nota_promedio_necesaria - 4.0,
            estrategias=estrategias
        )

    def _generar_estrategias(self, pendientes: List[Evaluacion], nota_req: float) -> List[EstrategiaDistribucion]:
        # Estrategia 1: Uniforme
        uniforme = EstrategiaDistribucion(
            nombre="Uniforme",
            descripcion=f"Mantener promedio de {nota_req:.2f}",
            distribuciones=[{"evaluacion": e.nombre, "nota_necesaria": round(nota_req, 2), "ponderacion": e.ponderacion_porcentaje} for e in pendientes],
            dificultad=self._clasificar_dificultad(nota_req)
        )
        # Estrategia 2: Realista
        nota_m = nota_req + 0.5
        realista = EstrategiaDistribucion(
            nombre="Realista con margen",
            descripcion="Apuntar a +0.5 para seguridad",
            distribuciones=[{"evaluacion": e.nombre, "nota_necesaria": round(min(nota_m, 7.0), 2), "ponderacion": e.ponderacion_porcentaje} for e in pendientes],
            dificultad=self._clasificar_dificultad(nota_m)
        )
        return [uniforme, realista]

    def _clasificar_dificultad(self, nota: float) -> str:
        if nota > 7.0: return "Imposible"
        if nota >= 6.0: return "Muy Difícil"
        if nota >= 5.0: return "Difícil"
        return "Moderado" if nota >= 4.0 else "Fácil"
```

---

## 4. IMPLEMENTACIÓN FRONTEND

### Tarea 4.1: Componente UI React (`CalculadoraNotas.tsx`)
```tsx
import React, { useState } from 'react';
import { useProyeccion } from '../hooks/useCalculadora';
import { Card, CardHeader, CardTitle, CardContent } from '@/shared/components/ui/card';
import { Slider } from '@/shared/components/ui/slider';

export function CalculadoraNotas({ cursoId, cursoNombre }: { cursoId: number, cursoNombre: string }) {
  const [notaObjetivo, setNotaObjetivo] = useState(5.5);
  const { data: p, isLoading } = useProyeccion(cursoId, notaObjetivo);

  if (isLoading) return <div className="p-4 animate-pulse">Analizando escenarios...</div>;

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-lg">{cursoNombre}</CardTitle>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">Nota Objetivo: {notaObjetivo.toFixed(1)}</p>
          <Slider 
            min={1} max={7} step={0.1} 
            value={[notaObjetivo]} 
            onValueChange={(v) => setNotaObjetivo(v[0])} 
          />
        </div>
      </CardHeader>
      {p && (
        <CardContent className="space-y-4">
          <div className={`p-3 rounded-lg text-center font-bold ${p.es_factible ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
            {p.es_factible ? 'ESCENARIO FACTIBLE' : 'ESCENARIO IMPOSIBLE'}
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="border p-2 rounded">Promedio Actual: <strong>{p.nota_actual.toFixed(2)}</strong></div>
            <div className="border p-2 rounded">Pendiente: <strong>{p.ponderacion_restante}%</strong></div>
          </div>
          {p.estrategias.map((est, i) => (
            <div key={i} className="text-xs border-l-4 border-primary p-2 bg-slate-50">
              <p className="font-bold">{est.nombre} — {est.dificultad}</p>
              {est.distribuciones.map((d, j) => (
                <div key={j} className="flex justify-between py-1 border-b last:border-0">
                  <span>{d.evaluacion} ({d.ponderacion}%)</span>
                  <span className="font-mono font-bold">{d.nota_necesaria}</span>
                </div>
              ))}
            </div>
          ))}
        </CardContent>
      )}
    </Card>
  );
}
```

---

## 5. REGLAS DEL AGENTE (PROTOCOLOS ANTIGRAVITY)

1.  **Zero-Tolerance de Alucinaciones**: No inventar campos en los DTOs que no existan en los modelos de base de datos definidos en el Sprint 1.
2.  **Arquitectura Limpia**: Los cálculos matemáticos residen **únicamente** en `CalculadoraService`. Los controladores solo delegan.
3.  **Invisibilidad de Personalización**: No justificar sugerencias basadas en datos personales (como el hecho de ser estudiante en INACAP). Ejecutar como una herramienta técnica neutra.
4.  **Respuesta Directa**: Priorizar bloques de código funcionales. Minimizar prosa explicativa.
5.  **Validación Robusta**: Todo cálculo que involucre notas debe validar el rango `[1.0 - 7.0]` (Escala Chilena) antes de procesar.
6.  **Eager Loading**: Siempre usar `selectinload` para cargar las evaluaciones de un curso y evitar el problema de N+1 consultas en SQLAlchemy.

---

**Estado del Sprint**: 🟢 Listos para implementación.
**Próximo Paso**: Copiar `calculadora_service.py` y correr `pytest`.