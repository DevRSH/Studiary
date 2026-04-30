import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cursoApi } from '../api/cursoApi';
import type { CursoCreateRequest, CursoUpdateRequest } from '../types';

export const useCursos = () => {
  return useQuery({
    queryKey: ['cursos'],
    queryFn: cursoApi.getAll,
  });
};

export const useCurso = (id: number) => {
  return useQuery({
    queryKey: ['cursos', id],
    queryFn: () => cursoApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateCurso = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CursoCreateRequest) => cursoApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cursos'] });
    },
  });
};

export const useUpdateCurso = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CursoUpdateRequest }) =>
      cursoApi.update(id, data),
    onSuccess: (_, variables) => {
      // Invalida la lista general y el caché específico de este curso
      queryClient.invalidateQueries({ queryKey: ['cursos'] });
      queryClient.invalidateQueries({ queryKey: ['cursos', variables.id] });
    },
  });
};

export const useDeleteCurso = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => cursoApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cursos'] });
    },
  });
};