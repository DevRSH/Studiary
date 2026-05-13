import { apiClient } from '@/shared/api/client';
import type { Nota, NotaDetail, NotaCreateRequest, NotaUpdateRequest, Dibujo } from '../types';

export const notaApi = {
  getAll: async (temaId?: number, search?: string): Promise<Nota[]> => {
    const { data } = await apiClient.get<Nota[]>('/notas', {
      params: { tema_id: temaId, search },
    });
    return data;
  },

  getById: async (id: number): Promise<NotaDetail> => {
    const { data } = await apiClient.get<NotaDetail>(`/notas/${id}`);
    return data;
  },

  create: async (nota: NotaCreateRequest): Promise<NotaDetail> => {
    const { data } = await apiClient.post<NotaDetail>('/notas', nota);
    return data;
  },

  update: async (id: number, updates: NotaUpdateRequest): Promise<NotaDetail> => {
    const { data } = await apiClient.put<NotaDetail>(`/notas/${id}`, updates);
    return data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/notas/${id}`);
  },

  addDibujo: async (
    notaId: number,
    canvasJson: string,
    thumbnail?: string
  ): Promise<Dibujo> => {
    const { data } = await apiClient.post<Dibujo>(`/notas/${notaId}/dibujos`, {
      canvas_json: canvasJson,
      thumbnail_base64: thumbnail,
      orden: 0,
    });
    return data;
  },
};
