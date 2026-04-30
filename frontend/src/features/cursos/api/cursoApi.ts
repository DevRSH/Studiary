import { apiClient } from '@/shared/api/client';
import type { Curso, CursoCreateRequest, CursoUpdateRequest } from '../types';

export const cursoApi = {
  getAll: async (): Promise<Curso[]> => {
    const { data } = await apiClient.get<Curso[]>('/cursos');
    return data;
  },
  getById: async (id: number): Promise<Curso> => {
    const { data } = await apiClient.get<Curso>(`/cursos/${id}`);
    return data;
  },
  create: async (curso: CursoCreateRequest): Promise<Curso> => {
    const { data } = await apiClient.post<Curso>('/cursos', curso);
    return data;
  },
  update: async (id: number, updates: CursoUpdateRequest): Promise<Curso> => {
    const { data } = await apiClient.put<Curso>(`/cursos/${id}`, updates);
    return data;
  },
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/cursos/${id}`);
  },
};
