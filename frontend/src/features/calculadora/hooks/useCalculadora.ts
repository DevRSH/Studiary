import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/shared/api/client';

export interface Proyeccion {
  curso_id: number;
  nota_objetivo: number;
  nota_actual: number;
  ponderacion_usada: number;
  ponderacion_restante: number;
  es_factible: boolean;
  margen_error: number;
  estrategias: Array<{
    nombre: string;
    descripcion: string;
    distribuciones: Array<{
      evaluacion: string;
      nota_necesaria: number;
      ponderacion: number;
    }>;
    dificultad: string;
  }>;
}

export function useProyeccion(cursoId: number, notaObjetivo: number) {
  return useQuery({
    queryKey: ['proyeccion', cursoId, notaObjetivo],
    queryFn: async () => {
      const response = await apiClient.get<Proyeccion>(
        `/calculadora/proyeccion/${cursoId}`,
        { params: { nota_objetivo: notaObjetivo } }
      );
      return response.data;
    },
    enabled: !!cursoId,
  });
}
