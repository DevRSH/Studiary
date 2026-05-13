export interface Evaluacion {
  id: number;
  curso_id: number;
  nombre: string;
  tipo: string;
  fecha: string;
  ponderacion_porcentaje: number;
  nota_obtenida: number | null;
  nota_minima: number;
  nota_maxima: number;
  estado: 'pendiente' | 'rendida' | 'corregida';
  created_at: string;
  updated_at: string;
}

export interface EvaluacionCreateRequest {
  curso_id: number;
  nombre: string;
  tipo?: string;
  fecha: string;
  ponderacion_porcentaje: number;
  nota_minima?: number;
  nota_maxima?: number;
}

export interface EvaluacionUpdateRequest {
  nombre?: string;
  tipo?: string;
  fecha?: string;
  ponderacion_porcentaje?: number;
  nota_minima?: number;
  nota_maxima?: number;
}

export interface EvaluacionNotaUpdateRequest {
  nota_obtenida: number;
}
