/**
 * Periodos dashboard page — Sprint 0 placeholder.
 * Full implementation in Sprint 1.
 */

import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import type { ReactElement } from 'react';
import { apiClient } from '@/shared/api/client';

interface Periodo {
  id: number;
  nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  activo?: boolean;
}

interface PeriodosResponse {
  items: Periodo[];
  total: number;
}

interface Curso {
  id: number;
  nombre: string;
  codigo: string | null;
  color: string;
  creditos: number;
}

interface Evaluacion {
  id: number;
  curso_id: number;
  nombre: string;
  fecha: string;
  ponderacion_porcentaje: number;
  nota_obtenida: number | null;
  estado: 'pendiente' | 'rendida' | 'corregida';
}

interface Nota {
  id: number;
  titulo: string;
  tipo: 'texto' | 'handwritten' | 'mixto';
  updated_at: string;
}

interface DashboardData {
  periodos: Periodo[];
  cursos: Curso[];
  evaluaciones: Evaluacion[];
  notas: Nota[];
}

async function fetchDashboardData(): Promise<DashboardData> {
  const [periodosResult, cursosResult, evaluacionesResult, notasResult] = await Promise.allSettled([
    apiClient.get<PeriodosResponse>('/periodos/'),
    apiClient.get<Curso[]>('/cursos'),
    apiClient.get<Evaluacion[]>('/evaluaciones'),
    apiClient.get<Nota[]>('/notas'),
  ]);

  return {
    periodos: periodosResult.status === 'fulfilled' ? periodosResult.value.data.items : [],
    cursos: cursosResult.status === 'fulfilled' ? cursosResult.value.data : [],
    evaluaciones: evaluacionesResult.status === 'fulfilled' ? evaluacionesResult.value.data : [],
    notas: notasResult.status === 'fulfilled' ? notasResult.value.data : [],
  };
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('es-CL', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value));
}

function daysUntil(value: string): number {
  const today = new Date();
  const target = new Date(value);
  today.setHours(0, 0, 0, 0);
  target.setHours(0, 0, 0, 0);
  return Math.ceil((target.getTime() - today.getTime()) / 86_400_000);
}

/**
 * Dashboard page showing academic periods.
 * Displays Studiary branding while Sprint 1 is implemented.
 */
export function PeriodosPage(): ReactElement {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboardData,
  });

  const dashboard = data ?? { periodos: [], cursos: [], evaluaciones: [], notas: [] };
  const periodoActivo = dashboard.periodos.find((periodo) => periodo.activo) ?? dashboard.periodos[0];
  const evaluacionesPendientes = dashboard.evaluaciones
    .filter((evaluacion) => evaluacion.estado === 'pendiente')
    .sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime())
    .slice(0, 4);
  const notasRecientes = [...dashboard.notas]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 3);
  const ponderacionPendiente = dashboard.evaluaciones
    .filter((evaluacion) => evaluacion.nota_obtenida === null)
    .reduce((total, evaluacion) => total + evaluacion.ponderacion_porcentaje, 0);

  return (
    <main className="min-h-screen bg-surface px-4 py-6 sm:px-6 lg:px-8">
      <section className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-5 rounded-3xl border border-white/10 bg-gradient-to-br from-primary-900/60 via-surface-100 to-surface p-6 shadow-2xl shadow-black/30 sm:p-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-primary-300">
                Centro de Comando Académico
              </p>
              <h1 className="mt-3 text-4xl font-black tracking-tight text-white sm:text-5xl">
                Studiary
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-white/60 sm:text-base">
                Gestiona periodos, cursos, evaluaciones, notas digitales y proyección de
                rendimiento desde una sola PWA.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => void refetch()}
                className="btn-ghost"
                disabled={isLoading}
              >
                {isLoading ? 'Actualizando…' : 'Actualizar'}
              </button>
              <Link to="/demo" className="btn-primary">
                Motor predictivo
              </Link>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="glass-card p-4">
              <span className="text-xs uppercase tracking-widest text-white/40">Periodos</span>
              <strong className="mt-2 block text-3xl text-white">{dashboard.periodos.length}</strong>
            </div>
            <div className="glass-card p-4">
              <span className="text-xs uppercase tracking-widest text-white/40">Cursos</span>
              <strong className="mt-2 block text-3xl text-white">{dashboard.cursos.length}</strong>
            </div>
            <div className="glass-card p-4">
              <span className="text-xs uppercase tracking-widest text-white/40">Evaluaciones</span>
              <strong className="mt-2 block text-3xl text-white">
                {dashboard.evaluaciones.length}
              </strong>
            </div>
            <div className="glass-card p-4">
              <span className="text-xs uppercase tracking-widest text-white/40">
                Ponderación pendiente
              </span>
              <strong className="mt-2 block text-3xl text-white">
                {ponderacionPendiente.toFixed(0)}%
              </strong>
            </div>
          </div>
        </header>

        {isError && (
          <div className="rounded-2xl border border-red-400/30 bg-red-500/10 p-4 text-sm text-red-100">
            No se pudo sincronizar el dashboard completo. Revisa que la API esté activa en
            localhost:8333.
          </div>
        )}

        <section className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
          <div className="glass-card p-5 sm:p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-white">Periodo actual</h2>
                <p className="text-sm text-white/45">Resumen académico activo</p>
              </div>
              <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">
                {periodoActivo ? 'Activo' : 'Sin periodo'}
              </span>
            </div>
            {periodoActivo ? (
              <div className="mt-6 rounded-2xl bg-white/[0.04] p-5">
                <h3 className="text-2xl font-black text-white">{periodoActivo.nombre}</h3>
                <p className="mt-2 text-sm text-white/50">
                  {formatDate(periodoActivo.fecha_inicio)} — {formatDate(periodoActivo.fecha_fin)}
                </p>
                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  <div className="rounded-xl bg-surface/60 p-4">
                    <span className="text-xs text-white/40">Cursos registrados</span>
                    <strong className="mt-1 block text-2xl text-white">
                      {dashboard.cursos.length}
                    </strong>
                  </div>
                  <div className="rounded-xl bg-surface/60 p-4">
                    <span className="text-xs text-white/40">Evaluaciones pendientes</span>
                    <strong className="mt-1 block text-2xl text-white">
                      {evaluacionesPendientes.length}
                    </strong>
                  </div>
                  <div className="rounded-xl bg-surface/60 p-4">
                    <span className="text-xs text-white/40">Notas digitales</span>
                    <strong className="mt-1 block text-2xl text-white">
                      {dashboard.notas.length}
                    </strong>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-6 rounded-2xl border border-dashed border-white/10 p-8 text-center text-white/50">
                Aún no hay periodos creados. Crea un periodo desde la API para comenzar.
              </div>
            )}
          </div>

          <div className="glass-card p-5 sm:p-6">
            <h2 className="text-xl font-bold text-white">Accesos rápidos</h2>
            <div className="mt-5 grid gap-3">
              <Link to="/demo" className="rounded-2xl bg-primary-500/15 p-4 transition hover:bg-primary-500/25">
                <span className="text-lg font-bold text-primary-200">Motor predictivo</span>
                <p className="mt-1 text-sm text-white/50">Proyecta notas objetivo por curso.</p>
              </Link>
              <div className="rounded-2xl bg-white/[0.04] p-4">
                <span className="text-lg font-bold text-white">Notas + handwriting</span>
                <p className="mt-1 text-sm text-white/50">
                  Apuntes Markdown y dibujos digitales conectados al backend.
                </p>
              </div>
              <div className="rounded-2xl bg-white/[0.04] p-4">
                <span className="text-lg font-bold text-white">PWA offline</span>
                <p className="mt-1 text-sm text-white/50">
                  Manifest, service worker e instalación local habilitados.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="glass-card p-5 sm:p-6">
            <h2 className="text-xl font-bold text-white">Próximas evaluaciones</h2>
            <div className="mt-5 space-y-3">
              {evaluacionesPendientes.length > 0 ? (
                evaluacionesPendientes.map((evaluacion) => {
                  const curso = dashboard.cursos.find((item) => item.id === evaluacion.curso_id);
                  const remainingDays = daysUntil(evaluacion.fecha);
                  return (
                    <article key={evaluacion.id} className="rounded-2xl bg-white/[0.04] p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <h3 className="font-bold text-white">{evaluacion.nombre}</h3>
                          <p className="mt-1 text-sm text-white/45">
                            {curso?.nombre ?? 'Curso sin identificar'} · {formatDate(evaluacion.fecha)}
                          </p>
                        </div>
                        <span className="rounded-full bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-200">
                          {remainingDays >= 0 ? `${remainingDays} días` : 'Vencida'}
                        </span>
                      </div>
                      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                        <div
                          className="h-full rounded-full bg-primary-400"
                          style={{ width: `${Math.min(evaluacion.ponderacion_porcentaje, 100)}%` }}
                        />
                      </div>
                    </article>
                  );
                })
              ) : (
                <p className="rounded-2xl border border-dashed border-white/10 p-6 text-center text-sm text-white/45">
                  No hay evaluaciones pendientes.
                </p>
              )}
            </div>
          </div>

          <div className="glass-card p-5 sm:p-6">
            <h2 className="text-xl font-bold text-white">Notas recientes</h2>
            <div className="mt-5 space-y-3">
              {notasRecientes.length > 0 ? (
                notasRecientes.map((nota) => (
                  <article key={nota.id} className="rounded-2xl bg-white/[0.04] p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <h3 className="font-bold text-white">{nota.titulo}</h3>
                        <p className="mt-1 text-sm text-white/45">
                          {nota.tipo} · actualizado {formatDate(nota.updated_at)}
                        </p>
                      </div>
                      <span className="rounded-full bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-200">
                        Nota
                      </span>
                    </div>
                  </article>
                ))
              ) : (
                <p className="rounded-2xl border border-dashed border-white/10 p-6 text-center text-sm text-white/45">
                  No hay notas registradas todavía.
                </p>
              )}
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}
