export type Rol = "colaborador" | "investigador";

export type EstadoAporte =
  | "pendiente_revision"
  | "aprobado"
  | "rechazado"
  | "correcciones_solicitadas";

export type EstadoFermentacion =
  | "semi_fermentado"
  | "fermentado"
  | "sobre_fermentado";

export type TipoNotificacion =
  | "aporte_aprobado"
  | "aporte_rechazado"
  | "correcciones_solicitadas"
  | "nuevo_aporte_pendiente";

export interface User {
  id: number;
  nombre: string;
  email: string;
  rol: Rol;
  created_at: string;
}

export interface Fermentacion {
  id: number;
  codigo: string;
  descripcion?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  created_at: string;
}

export interface MetadatoImagen {
  id: number;
  aporte_id: number;
  imagen: string;
  timestamp?: string;
  tiempo_horas?: number;
  glucosa_g_l?: number;
  fructosa_g_l?: number;
  sacarosa_g_l?: number;
  etanol_g_l?: number;
  acido_lactico_g_l?: number;
  acido_acetico_g_l?: number;
  acido_citrico_g_l?: number;
  acido_succinico_g_l?: number;
  acido_malico_g_l?: number;
  acido_oxalico_g_l?: number;
  acido_formico_g_l?: number;
  estado_fermentacion?: EstadoFermentacion;
  intervalo_incertidumbre_min?: number;
  validado_asesor: boolean;
  observaciones?: string;
  url_imagen?: string;
}

export interface Aporte {
  id: number;
  usuario_id: number;
  fermentacion_id: number;
  estado: EstadoAporte;
  observaciones?: string;
  fecha_subida: string;
  fecha_revision?: string;
  revisado_por?: number;
  ruta_minio?: string;
  fermentacion?: Fermentacion;
  usuario?: User;
  metadatos?: MetadatoImagen[];
}

export interface Notificacion {
  id: number;
  usuario_id: number;
  aporte_id?: number;
  tipo: TipoNotificacion;
  mensaje: string;
  leida: boolean;
  created_at: string;
}

export interface DatasetImagen {
  nombre: string;
  url: string;
  metadatos?: MetadatoImagen;
}

export interface DatasetAporte {
  id: number;
  fermentacion: Fermentacion;
  imagenes: DatasetImagen[];
  total_imagenes: number;
}
