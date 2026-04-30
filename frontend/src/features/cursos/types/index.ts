export interface Curso {
  id: number;
  periodo_id: number;
  nombre: string;
  codigo: string | null;
  color: string;
  creditos: number;
  created_at: string;
  updated_at: string;
}

export interface CursoCreateRequest {
  periodo_id: number;
  nombre: string;
  codigo?: string;
  color?: string;
  creditos?: number;
}

export type CursoUpdateRequest = Partial<CursoCreateRequest>;
