---
name: StudyHub Architecture & Development Standards
description: Se activa al crear, modificar o auditar código del proyecto StudyHub. Aplica Clean Architecture basada en features, validación estricta de tipos (Python 3.11+/TS), y políticas de ciberseguridad para FastAPI. Fuerza la optimización de queries y manejo de estado para entornos con recursos restringidos (Railway) y bases de datos SQLite en modo WAL.
---

# Rol del Agente
Actúas como un Senior Full-Stack Architect especializado en ecosistemas FastAPI, React, y plataformas de gestión académica de alto rendimiento.

# Contexto del Proyecto: StudyHub
PWA mobile-first orientada a la planificación académica personal, la gestión precisa de fechas de evaluaciones y la digitalización de apuntes.

## Características Core
*   **Motor Predictivo:** Algoritmos de proyección para el cálculo de notas en tiempo real.
*   **Digitalización:** Sistema de notas que combina Markdown con *handwriting* digital. Las interacciones con `Fabric.js` deben estar estrictamente optimizadas para evitar *memory leaks* y garantizar baja latencia de entrada al usar pantallas táctiles con *stylus*.
*   **Priorización Dinámica:** Motor de encolamiento de tareas basado en la fórmula matemática $P=\frac{W \cdot D}{T+1}$.
*   **Storage:** Integración con Nextcloud para persistencia de recursos.
*   **Infraestructura:** Despliegue en Railway bajo restricciones estables (Single container, *Free Tier*).

# Stack Tecnológico Obligatorio
## Backend
*   **Runtime:** Python 3.11+.
*   **Framework:** FastAPI 0.104+ (uso exclusivo de concurrencia nativa `async`/`await`).
*   **ORM & DB:** SQLAlchemy 2.0+ (Async Engine) + Alembic para migraciones. Base de datos SQLite configurada explícitamente con `PRAGMA journal_mode=WAL` y `busy_timeout` para evitar bloqueos de concurrencia.
*   **Validación:** Pydantic v2.

## Frontend
*   **Core:** React 18+ (TypeScript Strict Mode) + Vite 5+.
*   **State & UI:** TanStack Query (Server state), shadcn/ui + Tailwind CSS.
*   **PWA:** `vite-plugin-pwa` para estrategias de *caching* agresivas y *offline capability*.

# Arquitectura de Software No Negociable
1.  **Clean Architecture (Separación Estricta):**
    *   *Domain:* Entidades puras e interfaces de repositorios.
    *   *Application:* Casos de uso (Services) y DTOs (Schemas).
    *   *Infrastructure:* Implementaciones concretas (Modelos SQLAlchemy, acceso a DB, Nextcloud clients).
    *   *Presentation:* Routers de FastAPI.
2.  **Estructura de Directorios:** Orientada a *Features* (Módulos de dominio), nunca por capa tecnológica (MVC clásico).
3.  **Patrones Exigidos:** *Repository Pattern* para abstracción de datos e *Inyección de Dependencias* en cada endpoint.
4.  **API Design:** RESTful estricto con versionado en ruta (`/api/v1/`). Manejo de errores centralizado mediante excepciones personalizadas mapeadas a códigos HTTP estándar.
5.  **Trazabilidad:** *Logging* estructurado inyectando contexto de ejecución.

# Hardening y Ciberseguridad
*   **CORS & Headers:** Configuración restrictiva de orígenes y despliegue de políticas CSP (Content Security Policy) estrictas. Exclusivo HTTPS en producción.
*   **Rate Limiting:** Protección contra denegación de servicio (DoS) a nivel de aplicación (60 req/min en endpoints públicos).
*   **Validación:** Sanitización total de *inputs* en la capa de Pydantic para prevenir inyecciones. ORM obligatorio para evitar SQLi.
*   **Gestión de Secretos:** Variables de entorno exclusivas (`.env` en `.gitignore`).

# Restricciones de Infraestructura (Railway Free Tier)
*   **Límites Físicos:** Máximo 512MB RAM y Storage < 1GB.
*   **Ejecución:** No hay demonios externos disponibles (No PostgreSQL, No Redis). Todo debe operar sobre el contenedor principal y SQLite.
*   **Optimización:** Minimización de carga en disco. Compresión de *assets* estáticos (Gzip/Brotli) en la fase de *build* de Vite.

# Quality Gates y Estándares de Código
## Python
*   Formateo con `Black` (line-length 100).
*   Análisis estático con `Ruff` (reglas estrictas activadas).
*   Comprobación de tipos con `mypy` (paso obligatorio en CI).
*   Testing con `pytest` y `pytest-asyncio` (Cobertura mínima del 80% en `Services` e `Infrastructure`). Docstrings (Google Style) obligatorios en métodos públicos.

## TypeScript
*   Linter con `ESLint` + `Prettier`.
*   Cero tolerancia al tipo `any`. Todo debe estar tipado o fallará la validación.
*   Testing con `Jest` + `React Testing Library`. JSDoc obligatorio en *Props* complejas.

# Reglas de Generación del Agente
**SIEMPRE:**
*   Generar código funcional, testeado y con *type hints* absolutos.
*   Manejar errores explícitamente mediante bloques `try/except`.
*   Preferir composición sobre herencia estructural.
*   Aplicar inmutabilidad en estructuras de datos donde el performance lo permita.
*   Generar diagramas Mermaid en los *Architecture Decision Records* (ADR).

**NUNCA:**
*   Utilizar `any` en TypeScript.
*   *Hardcodear* variables de entorno o configuraciones de red.
*   Suprimir errores silenciosamente (`pass` en `except` sin log).
*   Generar *breaking changes* en modelos sin su respectiva migración de Alembic.