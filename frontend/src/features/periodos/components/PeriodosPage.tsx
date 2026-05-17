import { type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { ReactElement } from 'react';
import { apiClient } from '@/shared/api/client';

interface Periodo {
  id: number;
  nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  activo: boolean;
}

interface PeriodosResponse {
  items: Periodo[];
  total: number;
}

interface Curso {
  id: number;
  periodo_id: number;
  nombre: string;
  codigo: string;
  color: string;
  creditos: number;
}

interface Evaluacion {
  id: number;
  curso_id: number;
  nombre: string;
  tipo: string;
  fecha: string;
  ponderacion_porcentaje: number;
  nota_obtenida: number | null;
  estado: 'pendiente' | 'rendida' | 'corregida';
}

interface Nota {
  id: number;
  titulo: string;
  contenido_markdown: string | null;
  tipo: 'texto' | 'handwritten' | 'mixto';
  updated_at: string;
}

interface DashboardData {
  periodos: Periodo[];
  cursos: Curso[];
  evaluaciones: Evaluacion[];
  notas: Nota[];
}

interface PeriodoCreateRequest {
  nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  activo: boolean;
}

interface CursoCreateRequest {
  periodo_id: number;
  nombre: string;
  codigo: string;
  creditos: number;
  color: string;
}

interface EvaluacionCreateRequest {
  curso_id: number;
  nombre: string;
  tipo: string;
  fecha: string;
  ponderacion_porcentaje: number;
}

interface NotaCreateRequest {
  titulo: string;
  contenido_markdown: string;
  tipo: 'texto' | 'handwritten' | 'mixto';
}

async function fetchDashboardData(): Promise<DashboardData> {
  const [periodosResponse, cursosResponse, evaluacionesResponse, notasResponse] = await Promise.all([
    apiClient.get<PeriodosResponse>('/periodos/'),
    apiClient.get<Curso[]>('/cursos/'),
    apiClient.get<Evaluacion[]>('/evaluaciones/'),
    apiClient.get<Nota[]>('/notas/'),
  ]);

  return {
    periodos: periodosResponse.data.items,
    cursos: cursosResponse.data,
    evaluaciones: evaluacionesResponse.data,
    notas: notasResponse.data,
  };
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('es-CL', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value));
}

function getString(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === 'string' ? value.trim() : '';
}

function getNumber(formData: FormData, key: string): number {
  return Number(getString(formData, key));
}

function Field({
  label,
  name,
  type = 'text',
  defaultValue,
  min,
  max,
  step,
  required = true,
}: {
  label: string;
  name: string;
  type?: string;
  defaultValue?: string | number;
  min?: string | number;
  max?: string | number;
  step?: string | number;
  required?: boolean;
}): ReactElement {
  return (
    <label className="grid gap-2 text-sm text-white/70">
      <span>{label}</span>
      <input
        name={name}
        type={type}
        defaultValue={defaultValue}
        min={min}
        max={max}
        step={step}
        required={required}
        className="input-base"
      />
    </label>
  );
}

function SelectField({
  label,
  name,
  children,
}: {
  label: string;
  name: string;
  children: ReactElement | ReactElement[];
}): ReactElement {
  return (
    <label className="grid gap-2 text-sm text-white/70">
      <span>{label}</span>
      <select name={name} required className="input-base">
        {children}
      </select>
    </label>
  );
}

export function PeriodosPage(): ReactElement {
  const queryClient = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboardData,
  });

  const invalidateDashboard = async (): Promise<void> => {
    await queryClient.invalidateQueries({ queryKey: ['dashboard'] });
  };

  const createPeriodo = useMutation({
    mutationFn: (payload: PeriodoCreateRequest) => apiClient.post('/periodos/', payload),
    onSuccess: invalidateDashboard,
  });

  const createCurso = useMutation({
    mutationFn: (payload: CursoCreateRequest) => apiClient.post('/cursos/', payload),
    onSuccess: invalidateDashboard,
  });

  const createEvaluacion = useMutation({
    mutationFn: (payload: EvaluacionCreateRequest) => apiClient.post('/evaluaciones/', payload),
    onSuccess: invalidateDashboard,
  });

  const createNota = useMutation({
    mutationFn: (payload: NotaCreateRequest) => apiClient.post('/notas/', payload),
    onSuccess: invalidateDashboard,
  });

  const dashboard = data ?? { periodos: [], cursos: [], evaluaciones: [], notas: [] };
  const periodoActivo = dashboard.periodos.find((periodo) => periodo.activo) ?? dashboard.periodos[0];
  const evaluacionesPendientes = dashboard.evaluaciones
    .filter((evaluacion) => evaluacion.estado === 'pendiente')
    .sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());
  const notasRecientes = [...dashboard.notas].sort(
    (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  );

  const handlePeriodoSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    createPeriodo.mutate(
      {
        nombre: getString(formData, 'nombre'),
        fecha_inicio: getString(formData, 'fecha_inicio'),
        fecha_fin: getString(formData, 'fecha_fin'),
        activo: true,
      },
      { onSuccess: () => form.reset() }
    );
  };

  const handleCursoSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    createCurso.mutate(
      {
        periodo_id: getNumber(formData, 'periodo_id'),
        nombre: getString(formData, 'nombre'),
        codigo: getString(formData, 'codigo'),
        creditos: getNumber(formData, 'creditos'),
        color: getString(formData, 'color') || '#6366f1',
      },
      { onSuccess: () => form.reset() }
    );
  };

  const handleEvaluacionSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    createEvaluacion.mutate(
      {
        curso_id: getNumber(formData, 'curso_id'),
        nombre: getString(formData, 'nombre'),
        tipo: getString(formData, 'tipo'),
        fecha: getString(formData, 'fecha'),
        ponderacion_porcentaje: getNumber(formData, 'ponderacion_porcentaje'),
      },
      { onSuccess: () => form.reset() }
    );
  };

  const handleNotaSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    createNota.mutate(
      {
        titulo: getString(formData, 'titulo'),
        contenido_markdown: getString(formData, 'contenido_markdown'),
        tipo: getString(formData, 'tipo') as NotaCreateRequest['tipo'],
      },
      { onSuccess: () => form.reset() }
    );
  };

  return (
    <main className="min-h-screen bg-surface px-4 py-6 sm:px-6 lg:px-8">
      <section className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <header className="rounded-3xl border border-white/10 bg-gradient-to-br from-primary-900/70 via-surface-100 to-surface p-6 shadow-2xl shadow-black/30 sm:p-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-primary-300">
                Centro de Comando Académico
              </p>
              <h1 className="mt-3 text-4xl font-black tracking-tight text-white sm:text-5xl">
                Studiary
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-white/60 sm:text-base">
                Frontend funcional para gestionar periodos, cursos, evaluaciones, notas y acceder al motor predictivo.
              </p>
            </div>
            <Link to="/demo" className="btn-primary w-fit">
              Motor predictivo
            </Link>
          </div>
          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="glass-card p-4"><span className="text-xs uppercase tracking-widest text-white/40">Periodos</span><strong className="mt-2 block text-3xl text-white">{dashboard.periodos.length}</strong></div>
            <div className="glass-card p-4"><span className="text-xs uppercase tracking-widest text-white/40">Cursos</span><strong className="mt-2 block text-3xl text-white">{dashboard.cursos.length}</strong></div>
            <div className="glass-card p-4"><span className="text-xs uppercase tracking-widest text-white/40">Evaluaciones</span><strong className="mt-2 block text-3xl text-white">{dashboard.evaluaciones.length}</strong></div>
            <div className="glass-card p-4"><span className="text-xs uppercase tracking-widest text-white/40">Notas</span><strong className="mt-2 block text-3xl text-white">{dashboard.notas.length}</strong></div>
          </div>
        </header>

        {isError && <div className="rounded-2xl border border-red-400/30 bg-red-500/10 p-4 text-sm text-red-100">No se pudo cargar la consola académica. Verifica que el backend esté activo en localhost:8333.</div>}

        <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <div className="glass-card p-5 sm:p-6">
            <h2 className="text-xl font-bold text-white">Crear datos académicos</h2>
            <div className="mt-5 grid gap-5">
              <form onSubmit={handlePeriodoSubmit} className="rounded-2xl bg-white/[0.04] p-4">
                <h3 className="font-bold text-white">Nuevo periodo</h3>
                <div className="mt-4 grid gap-3 sm:grid-cols-3"><Field label="Nombre" name="nombre" defaultValue="Semestre 2026-I" /><Field label="Inicio" name="fecha_inicio" type="date" /><Field label="Fin" name="fecha_fin" type="date" /></div>
                <button type="submit" className="btn-primary mt-4" disabled={createPeriodo.isPending}>Crear periodo</button>
              </form>

              <form onSubmit={handleCursoSubmit} className="rounded-2xl bg-white/[0.04] p-4">
                <h3 className="font-bold text-white">Nuevo curso</h3>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <SelectField label="Periodo" name="periodo_id">{dashboard.periodos.map((periodo) => <option key={periodo.id} value={periodo.id}>{periodo.nombre}</option>)}</SelectField>
                  <Field label="Nombre" name="nombre" defaultValue="Cálculo Diferencial" /><Field label="Código" name="codigo" defaultValue="MAT-101" /><Field label="Créditos" name="creditos" type="number" min={1} max={20} defaultValue={4} /><Field label="Color" name="color" type="color" defaultValue="#6366f1" />
                </div>
                <button type="submit" className="btn-primary mt-4" disabled={!dashboard.periodos.length || createCurso.isPending}>Crear curso</button>
              </form>

              <form onSubmit={handleEvaluacionSubmit} className="rounded-2xl bg-white/[0.04] p-4">
                <h3 className="font-bold text-white">Nueva evaluación</h3>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <SelectField label="Curso" name="curso_id">{dashboard.cursos.map((curso) => <option key={curso.id} value={curso.id}>{curso.nombre}</option>)}</SelectField>
                  <Field label="Nombre" name="nombre" defaultValue="Solemne 1" /><Field label="Tipo" name="tipo" defaultValue="solemne" /><Field label="Fecha" name="fecha" type="date" /><Field label="Ponderación %" name="ponderacion_porcentaje" type="number" min={1} max={100} step={0.1} defaultValue={25} />
                </div>
                <button type="submit" className="btn-primary mt-4" disabled={!dashboard.cursos.length || createEvaluacion.isPending}>Crear evaluación</button>
              </form>

              <form onSubmit={handleNotaSubmit} className="rounded-2xl bg-white/[0.04] p-4">
                <h3 className="font-bold text-white">Nueva nota</h3>
                <div className="mt-4 grid gap-3">
                  <Field label="Título" name="titulo" defaultValue="Apunte de clase" />
                  <SelectField label="Tipo" name="tipo"><option value="texto">Texto</option><option value="handwritten">Handwriting</option><option value="mixto">Mixto</option></SelectField>
                  <label className="grid gap-2 text-sm text-white/70"><span>Contenido Markdown</span><textarea name="contenido_markdown" rows={4} className="input-base" defaultValue="## Resumen" /></label>
                </div>
                <button type="submit" className="btn-primary mt-4" disabled={createNota.isPending}>Crear nota</button>
              </form>
            </div>
          </div>

          <div className="grid gap-6">
            <section className="glass-card p-5 sm:p-6"><div className="flex items-center justify-between"><h2 className="text-xl font-bold text-white">Periodo actual</h2><span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">{periodoActivo ? 'Activo' : 'Sin periodo'}</span></div>{isLoading ? <p className="mt-5 text-sm text-white/50">Cargando datos académicos…</p> : periodoActivo ? <div className="mt-5 rounded-2xl bg-white/[0.04] p-4"><h3 className="text-2xl font-black text-white">{periodoActivo.nombre}</h3><p className="mt-2 text-sm text-white/50">{formatDate(periodoActivo.fecha_inicio)} — {formatDate(periodoActivo.fecha_fin)}</p></div> : <p className="mt-5 rounded-2xl border border-dashed border-white/10 p-6 text-center text-sm text-white/45">Crea un periodo para iniciar tu planificación.</p>}</section>

            <section className="glass-card p-5 sm:p-6"><h2 className="text-xl font-bold text-white">Cursos</h2><div className="mt-5 grid gap-3 sm:grid-cols-2">{dashboard.cursos.map((curso) => <article key={curso.id} className="rounded-2xl bg-white/[0.04] p-4"><div className="mb-3 h-2 rounded-full" style={{ backgroundColor: curso.color }} /><h3 className="font-bold text-white">{curso.nombre}</h3><p className="mt-1 text-sm text-white/45">{curso.codigo || 'Sin código'} · {curso.creditos} créditos</p></article>)}{!dashboard.cursos.length && <p className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-white/45">No hay cursos registrados.</p>}</div></section>

            <section className="glass-card p-5 sm:p-6"><h2 className="text-xl font-bold text-white">Próximas evaluaciones</h2><div className="mt-5 space-y-3">{evaluacionesPendientes.map((evaluacion) => { const curso = dashboard.cursos.find((item) => item.id === evaluacion.curso_id); return <article key={evaluacion.id} className="rounded-2xl bg-white/[0.04] p-4"><div className="flex items-start justify-between gap-4"><div><h3 className="font-bold text-white">{evaluacion.nombre}</h3><p className="mt-1 text-sm text-white/45">{curso?.nombre ?? 'Curso'} · {formatDate(evaluacion.fecha)}</p></div><span className="rounded-full bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-200">{evaluacion.ponderacion_porcentaje}%</span></div></article>; })}{!evaluacionesPendientes.length && <p className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-white/45">No hay evaluaciones pendientes.</p>}</div></section>

            <section className="glass-card p-5 sm:p-6"><h2 className="text-xl font-bold text-white">Notas recientes</h2><div className="mt-5 space-y-3">{notasRecientes.map((nota) => <article key={nota.id} className="rounded-2xl bg-white/[0.04] p-4"><h3 className="font-bold text-white">{nota.titulo}</h3><p className="mt-1 text-sm text-white/45">{nota.tipo} · {formatDate(nota.updated_at)}</p>{nota.contenido_markdown && <p className="mt-3 line-clamp-2 text-sm text-white/55">{nota.contenido_markdown}</p>}</article>)}{!notasRecientes.length && <p className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-white/45">No hay notas registradas.</p>}</div></section>
          </div>
        </section>
      </section>
    </main>
  );
}
