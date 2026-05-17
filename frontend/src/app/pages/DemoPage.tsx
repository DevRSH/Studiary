/**
 * DemoPage - Página de demostración permanente para Studiary
 * 
 * Esta página sirve como playground para probar el motor predictivo
 * y otras funcionalidades sin necesidad de crear datos manualmente.
 * 
 * URL: /demo
 */

import { useState, useEffect } from 'react';
import { apiClient } from '@shared/api/client';

// Datos de prueba - función para generar únicos cada vez
const generateDemoData = () => ({
  periodo: {
    nombre: `2026-I Demo ${Date.now()}`,
    fecha_inicio: '2026-03-01',
    fecha_fin: '2026-07-15',
    activo: true,
  },
  curso: {
    nombre: 'Cálculo Diferencial',
    codigo: 'MAT-101',
    creditos: 4,
    color: '#6366f1',
  },
  evaluaciones: [
    { nombre: 'Solemne 1', tipo: 'solemne', fecha: '2026-04-15', ponderacion_porcentaje: 25 },
    { nombre: 'Solemne 2', tipo: 'solemne', fecha: '2026-05-20', ponderacion_porcentaje: 25 },
    { nombre: 'Proyecto', tipo: 'proyecto', fecha: '2026-06-10', ponderacion_porcentaje: 20 },
    { nombre: 'Examen Final', tipo: 'examen', fecha: '2026-07-05', ponderacion_porcentaje: 30 },
  ],
});

export function DemoPage(): React.ReactElement {
  const [status, setStatus] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [error, setError] = useState<string>('');
  const [data, setData] = useState<{ periodoId?: number; cursoId?: number; evaluaciones?: number[] }>({});
  const [notaObjetivo, setNotaObjetivo] = useState<number>(5.0);
  const [proyeccion, setProyeccion] = useState<any>(null);
  const [loadingProyeccion, setLoadingProyeccion] = useState(false);

  // Cargar datos de prueba automáticamente al montar
  useEffect(() => {
    if (status === 'idle') {
      cargarDatosDemo();
    }
  }, [status]);

  const cargarDatosDemo = async () => {
    setStatus('loading');
    setError('');

    try {
      // 1. Crear periodo
      const periodoRes = await apiClient.post('/periodos/', generateDemoData().periodo);
      const periodoId = periodoRes.data.id;

      // 2. Crear curso
      const cursoRes = await apiClient.post('/cursos/', {
        ...generateDemoData().curso,
        periodo_id: periodoId,
      });
      const cursoId = cursoRes.data.id;

      // 3. Crear evaluaciones
      const evalIds: number[] = [];
      for (const evalData of generateDemoData().evaluaciones) {
        const evalRes = await apiClient.post('/evaluaciones/', {
          ...evalData,
          curso_id: cursoId,
        });
        evalIds.push(evalRes.data.id);
      }

      setData({ periodoId, cursoId, evaluaciones: evalIds });
      setStatus('ready');
      
      // Cargar proyección inicial
      await calcularProyeccion(cursoId, 5.0);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error desconocido');
      setStatus('error');
    }
  };

  const calcularProyeccion = async (cursoId: number, nota: number) => {
    setLoadingProyeccion(true);
    try {
      const res = await apiClient.get(`/calculadora/proyeccion/${cursoId}`, {
        params: { nota_objetivo: nota },
      });
      setProyeccion(res.data);
    } catch (err) {
      console.error('Error calculando proyección:', err);
    } finally {
      setLoadingProyeccion(false);
    }
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const nota = parseFloat(e.target.value);
    setNotaObjetivo(nota);
    if (data.cursoId) {
      calcularProyeccion(data.cursoId, nota);
    }
  };

  const ingresarNota = async (evaluacionId: number, nota: number) => {
    try {
      await apiClient.patch(`/evaluaciones/${evaluacionId}/nota`, {
        nota_obtenida: nota,
      });
      // Recalcular proyección
      if (data.cursoId) {
        await calcularProyeccion(data.cursoId, notaObjetivo);
      }
    } catch (err) {
      console.error('Error ingresando nota:', err);
    }
  };

  const limpiarDatos = async () => {
    if (!window.confirm('¿Eliminar todos los datos de demo?')) return;
    
    try {
      if (data.cursoId) {
        await apiClient.delete(`/cursos/${data.cursoId}`);
      }
      if (data.periodoId) {
        await apiClient.delete(`/periodos/${data.periodoId}`);
      }
      setData({});
      setProyeccion(null);
      setStatus('idle');
    } catch (err) {
      console.error('Error limpiando datos:', err);
    }
  };

  // Render
  return (
    <div className="min-h-screen bg-surface p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🎮</span>
            <h1 className="text-2xl font-bold text-white">Demo - Motor Predictivo</h1>
          </div>
          <p className="text-white/60 text-sm">
            Página de demostración permanente. Usa datos de prueba para probar el calculador de notas.
          </p>
          <div className="flex gap-2 mt-4">
            <a 
              href="/" 
              className="text-xs text-primary-400 hover:text-primary-300 underline"
            >
              ← Volver al inicio
            </a>
            <span className="text-white/30">|</span>
            <a 
              href="/docs" 
              target="_blank" 
              rel="noreferrer"
              className="text-xs text-primary-400 hover:text-primary-300 underline"
            >
              API Docs →
            </a>
          </div>
        </div>

        {/* Status */}
        {status === 'loading' && (
          <div className="bg-surface-variant/50 rounded-xl p-8 text-center">
            <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-white/70">Cargando datos de prueba...</p>
          </div>
        )}

        {status === 'error' && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 mb-6">
            <h3 className="text-red-400 font-semibold mb-2">Error</h3>
            <p className="text-white/70 text-sm mb-4">{error}</p>
            <button 
              onClick={cargarDatosDemo}
              className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg text-sm transition-colors"
            >
              Reintentar
            </button>
          </div>
        )}

        {status === 'ready' && data.cursoId && (
          <>
            {/* Info Card */}
            <div className="bg-surface-variant/50 rounded-xl p-6 mb-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-white">{generateDemoData().curso.nombre}</h2>
                  <p className="text-white/60 text-sm">{generateDemoData().curso.codigo} • {generateDemoData().periodo.nombre}</p>
                </div>
                <button
                  onClick={limpiarDatos}
                  className="text-xs text-red-400 hover:text-red-300 underline"
                >
                  Limpiar datos
                </button>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-surface/50 rounded-lg p-3">
                  <span className="text-white/50 block text-xs">Evaluaciones</span>
                  <span className="text-white font-semibold">{data.evaluaciones?.length || 0}</span>
                </div>
                <div className="bg-surface/50 rounded-lg p-3">
                  <span className="text-white/50 block text-xs">Ponderación Total</span>
                  <span className="text-white font-semibold">100%</span>
                </div>
                <div className="bg-surface/50 rounded-lg p-3">
                  <span className="text-white/50 block text-xs">Curso ID</span>
                  <span className="text-white font-mono text-xs">{data.cursoId}</span>
                </div>
                <div className="bg-surface/50 rounded-lg p-3">
                  <span className="text-white/50 block text-xs">Status</span>
                  <span className="text-emerald-400 text-xs">✓ Listo</span>
                </div>
              </div>
            </div>

            {/* Calculadora */}
            <div className="bg-surface-variant/50 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span>🎯</span> Calculadora de Proyección
              </h3>

              {/* Slider */}
              <div className="mb-6">
                <label className="block text-sm text-white/70 mb-2">
                  Nota Objetivo: <span className="text-primary-400 font-semibold text-lg">{notaObjetivo.toFixed(1)}</span>
                </label>
                <input
                  type="range"
                  min="1.0"
                  max="7.0"
                  step="0.1"
                  value={notaObjetivo}
                  onChange={handleSliderChange}
                  className="w-full h-2 bg-surface rounded-lg appearance-none cursor-pointer accent-primary-500"
                />
                <div className="flex justify-between text-xs text-white/40 mt-1">
                  <span>1.0</span>
                  <span>4.0</span>
                  <span>7.0</span>
                </div>
              </div>

              {/* Resultado */}
              {loadingProyeccion ? (
                <div className="text-center py-8">
                  <div className="animate-spin w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full mx-auto" />
                </div>
              ) : proyeccion ? (
                <div className="space-y-4">
                  {/* Factibilidad */}
                  <div className={`p-4 rounded-lg ${proyeccion.es_factible ? 'bg-emerald-500/10 border border-emerald-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{proyeccion.es_factible ? '✅' : '❌'}</span>
                      <span className={`font-semibold ${proyeccion.es_factible ? 'text-emerald-400' : 'text-red-400'}`}>
                        {proyeccion.es_factible ? 'Objetivo Factible' : 'Objetivo Imposible'}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-white/50 block">Nota Actual</span>
                        <span className="text-white font-semibold">{proyeccion.nota_actual?.toFixed(2) || '0.00'}</span>
                      </div>
                      <div>
                        <span className="text-white/50 block">Ponderación Usada</span>
                        <span className="text-white font-semibold">{proyeccion.ponderacion_usada?.toFixed(0) || 0}%</span>
                      </div>
                      <div>
                        <span className="text-white/50 block">Ponderación Restante</span>
                        <span className="text-white font-semibold">{proyeccion.ponderacion_restante?.toFixed(0) || 0}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Estrategias */}
                  {proyeccion.estrategias && proyeccion.estrategias.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="text-sm font-semibold text-white/70">Estrategias Recomendadas</h4>
                      {proyeccion.estrategias.map((estrategia: any, idx: number) => (
                        <div key={idx} className="bg-surface/50 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h5 className="text-white font-medium">{estrategia.nombre}</h5>
                              <p className="text-white/50 text-xs">{estrategia.descripcion}</p>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded ${
                              estrategia.dificultad === 'Fácil' ? 'bg-emerald-500/20 text-emerald-400' :
                              estrategia.dificultad === 'Moderado' ? 'bg-yellow-500/20 text-yellow-400' :
                              estrategia.dificultad === 'Difícil' ? 'bg-orange-500/20 text-orange-400' :
                              'bg-red-500/20 text-red-400'
                            }`}>
                              {estrategia.dificultad}
                            </span>
                          </div>
                          <div className="space-y-2">
                            {estrategia.distribuciones.map((dist: any, didx: number) => (
                              <div key={didx} className="flex justify-between items-center text-sm">
                                <span className="text-white/70">{dist.evaluacion}</span>
                                <div className="flex items-center gap-2">
                                  <span className="text-white/50 text-xs">({dist.ponderacion}%)</span>
                                  <span className="text-primary-400 font-semibold">{dist.nota_necesaria}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-white/50 text-center py-4">Mueve el slider para calcular proyección</p>
              )}
            </div>

            {/* Evaluaciones */}
            <div className="bg-surface-variant/50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Evaluaciones del Demo</h3>
              <div className="grid gap-3">
                {generateDemoData().evaluaciones.map((evalData, idx) => (
                  <div key={idx} className="bg-surface/50 rounded-lg p-4 flex justify-between items-center">
                    <div>
                      <h4 className="text-white font-medium">{evalData.nombre}</h4>
                      <p className="text-white/50 text-xs">{evalData.tipo} • {evalData.ponderacion_porcentaje}%</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-white/50 text-xs">Nota:</span>
                      <button
                        onClick={() => ingresarNota(data.evaluaciones![idx], 5.5)}
                        className="px-3 py-1 bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 rounded text-xs transition-colors"
                      >
                        5.5
                      </button>
                      <button
                        onClick={() => ingresarNota(data.evaluaciones![idx], 6.0)}
                        className="px-3 py-1 bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 rounded text-xs transition-colors"
                      >
                        6.0
                      </button>
                      <button
                        onClick={() => ingresarNota(data.evaluaciones![idx], 7.0)}
                        className="px-3 py-1 bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 rounded text-xs transition-colors"
                      >
                        7.0
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-white/40 text-xs mt-4">
                ℹ️ Haz clic en una nota para simular que rendiste una evaluación. La proyección se recalculará automáticamente.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
