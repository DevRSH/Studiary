import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { evaluacionApi } from '../api/evaluacionApi';
import type {
  EvaluacionCreateRequest,
  EvaluacionUpdateRequest,
  EvaluacionNotaUpdateRequest,
} from '../types';

export const useEvaluaciones = (cursoId?: number) => {
  return useQuery({
    queryKey: ['evaluaciones', cursoId],
    queryFn: () => evaluacionApi.getAll(cursoId),
  });
};

export const useEvaluacion = (id: number) => {
  return useQuery({
    queryKey: ['evaluaciones', id],
    queryFn: () => evaluacionApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateEvaluacion = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: EvaluacionCreateRequest) => evaluacionApi.create(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['evaluaciones'] });
      queryClient.invalidateQueries({ queryKey: ['evaluaciones', variables.curso_id] });
    },
  });
};

export const useUpdateEvaluacion = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: EvaluacionUpdateRequest }) =>
      evaluacionApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['evaluaciones'] });
      queryClient.invalidateQueries({ queryKey: ['evaluaciones', variables.id] });
    },
  });
};

export const useUpdateNota = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, nota }: { id: number; nota: EvaluacionNotaUpdateRequest }) =>
      evaluacionApi.updateNota(id, nota),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['evaluaciones'] });
      queryClient.invalidateQueries({ queryKey: ['evaluaciones', variables.id] });
    },
  });
};
