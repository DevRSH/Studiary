export type TipoNota = 'texto' | 'handwritten' | 'mixto';

export interface Dibujo {
  id: number;
  nota_id: number;
  canvas_json: string;
  thumbnail_base64: string | null;
  orden: number;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: number;
  nombre: string;
  color: string;
  created_at: string;
}

export interface Nota {
  id: number;
  tema_id: number | null;
  titulo: string;
  contenido_markdown: string | null;
  tipo: TipoNota;
  created_at: string;
  updated_at: string;
}

export interface NotaDetail extends Nota {
  dibujos: Dibujo[];
  tags: Tag[];
}

export interface DibujoCreateRequest {
  canvas_json: string;
  thumbnail_base64?: string;
  orden: number;
}

export interface NotaCreateRequest {
  tema_id?: number;
  titulo: string;
  contenido_markdown?: string;
  tipo: TipoNota;
  tag_ids?: number[];
  dibujos?: DibujoCreateRequest[];
}

export interface NotaUpdateRequest {
  tema_id?: number | null;
  titulo?: string;
  contenido_markdown?: string | null;
  tipo?: TipoNota;
  tag_ids?: number[];
}

export interface TagCreateRequest {
  nombre: string;
  color?: string;
}
