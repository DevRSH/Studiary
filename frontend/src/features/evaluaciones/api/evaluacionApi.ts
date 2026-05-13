import { apiClient } from '@/shared/api/client';
import type {
  Evaluacion,
  EvaluacionCreateRequest,
  EvaluacionUpdateRequest,
  EvaluacionNotaUpdateRequest,
} from '../types';

export const evaluacionApi = {
  getAll: async (cursoId?: number): Promise<Evaluacion[]> => {
    const { data } = await apiClient.get<Evaluacion[]>('/evaluaciones', {
      params: cursoId ? { curso_id: cursoId } : {},
    });
    return data;
  },

  getById: async (id: number): Promise<Evaluacion> => {
    const { data } = await apiClient.get<Evaluacion>(`/evaluaciones/${id}`);
    return data;
  },

  create: async (evaluacion: EvaluacionCreateRequest): Promise<Evaluacion> => {
    const { data } = await apiClient.post<Evaluacion>('/evaluaciones', evaluacion);
    return data;
  },

  update: async (id: number, updates: EvaluacionUpdateRequest): Promise<Evaluacion> => {
    const { data } = await apiClient.put<Evaluacion>(`/evaluaciones/${id}`, updates);
    return data;
  },

  updateNota: async (id: number, nota: EvaluacionNotaUpdateRequest): Promise<Evaluacion> => {
    const { data } = await apiClient.patch<Evaluacion>(`/evaluaciones/${id}/nota`, nota);
    return data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/evaluaciones/${id}`);
  },
};
