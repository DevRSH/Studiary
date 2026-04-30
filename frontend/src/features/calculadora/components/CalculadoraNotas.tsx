import React, { useState } from 'react';
import { useProyeccion } from '../hooks/useCalculadora';
import { Card, CardHeader, CardTitle, CardContent } from '@/shared/components/ui/card';
import { Slider } from '@/shared/components/ui/slider';

export function CalculadoraNotas({ cursoId, cursoNombre }: { cursoId: number, cursoNombre: string }) {
  const [notaObjetivo, setNotaObjetivo] = useState(5.5);
  const { data: p, isLoading, isError, error } = useProyeccion(cursoId, notaObjetivo);

  if (isLoading) return <div className="p-4 animate-pulse bg-slate-100 rounded-xl text-center">Analizando escenarios académicos...</div>;

  if (isError) {
    return (
      <Card className="w-full max-w-md border-red-200">
        <CardContent className="p-4 text-center text-red-600">
          <p className="font-bold">Error al calcular proyección</p>
          <p className="text-xs">{(error as Error)?.message || 'Ocurrió un error inesperado'}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md shadow-lg border-slate-100">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl font-bold text-slate-800">{cursoNombre}</CardTitle>
        <div className="space-y-4 mt-2">
          <div className="flex justify-between items-center">
             <p className="text-sm font-medium text-slate-600">Meta Académica</p>
             <p className="text-lg font-bold text-primary">{notaObjetivo.toFixed(1)}</p>
          </div>
          <Slider 
            min={1} max={7} step={0.1} 
            value={[notaObjetivo]} 
            onValueChange={(v) => setNotaObjetivo(v[0])}
            className="py-2"
          />
        </div>
      </CardHeader>
      {p && (
        <CardContent className="space-y-4 pt-2">
          <div className={`p-4 rounded-xl text-center font-black tracking-tight ${p.es_factible ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
            {p.es_factible ? '✨ ESCENARIO FACTIBLE' : '⚠️ ESCENARIO IMPOSIBLE'}
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <p className="text-slate-500 text-xs mb-1">Promedio Actual</p>
              <strong className="text-lg">{p.nota_actual.toFixed(2)}</strong>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <p className="text-slate-500 text-xs mb-1">Carga Pendiente</p>
              <strong className="text-lg">{p.ponderacion_restante}%</strong>
            </div>
          </div>
          {p.estrategias.length > 0 ? (
            <div className="space-y-3">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Estrategias de Esfuerzo</p>
              {p.estrategias.map((est, i) => (
                <div key={i} className="text-xs border border-slate-100 rounded-xl p-3 bg-white shadow-sm">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-bold text-slate-700 text-sm">{est.nombre}</p>
                      <p className="text-slate-500 text-[10px] leading-tight">{est.descripcion}</p>
                    </div>
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${
                      est.dificultad === 'Imposible' ? 'bg-red-100 text-red-600' :
                      est.dificultad === 'Muy Difícil' ? 'bg-orange-100 text-orange-600' :
                      est.dificultad === 'Difícil' ? 'bg-yellow-100 text-yellow-600' :
                      'bg-blue-100 text-blue-600'
                    }`}>
                      {est.dificultad.toUpperCase()}
                    </span>
                  </div>
                  <div className="space-y-1 mt-2">
                    {est.distribuciones.map((d, j) => (
                      <div key={j} className="flex justify-between py-1.5 border-t border-slate-50 first:border-0">
                        <span className="text-slate-600">{d.evaluacion} <span className="text-[10px] opacity-60">({d.ponderacion}%)</span></span>
                        <span className="font-mono font-black text-slate-800 text-sm">{d.nota_necesaria.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
             <div className="text-center p-4 bg-slate-50 rounded-xl border border-dashed border-slate-200">
               <p className="text-xs text-slate-500">No hay evaluaciones pendientes para proyectar.</p>
             </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}
