export interface Usuario {
  id: number;
  email: string;
  nombre: string;
  apellido: string;
  estado: 'ACTIVA' | 'INACTIVA';
  fecha_registro?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LibroISBNResponse {
  isbn: string;
  titulo: string;
  autores: string[];
  editorial: string | null;
  fecha_publicacion: string | null;
  sinopsis: string | null;
  generos: string[];
  portada_url: string | null;
}

export interface Autor {
  id: number;
  nombre: string;
}

export interface Editorial {
  id: number;
  nombre: string;
}

export interface Genero {
  id: number;
  nombre: string;
}

export interface Libro {
  id: number;
  isbn: string | null;
  titulo: string;
  autores: Autor[];
  editorial: Editorial | null;
  fecha_publicacion: string | null;
  sinopsis: string | null;
  generos: Genero[];
  portada_url: string | null;
  cantidad_ejemplares?: number;
}

export type EstadoLectura = 'PENDIENTE' | 'EN_CURSO' | 'LEIDO' | 'ABANDONADO';
export type CondicionFisica = 'NUEVO' | 'MUY_BUENO' | 'BUENO' | 'REGULAR' | 'DETERIORADO';

export interface Ejemplar {
  id: number;
  libro_id: number;
  libro?: Libro;
  estante_id: number | null;
  estado_fisico: CondicionFisica | null;
  fecha_adquisicion: string | null;
  precio_compra: number | null;
  moneda: string | null;
  observacion: string | null;
  activo: boolean;
}

export interface Estante {
  id: number;
  biblioteca_id: number;
  nombre: string;
  capacidad: number;
}

export interface Biblioteca {
  id: number;
  usuario_id: number;
  nombre: string;
  estantes: Estante[];
}

export type EstadoPrestamo = 'ACTIVO' | 'DEVUELTO' | 'VENCIDO' | 'CANCELADO';

export interface Prestamo {
  id: number;
  ejemplar_id: number;
  nombre_destinatario: string;
  apellido_destinatario: string;
  telefono_destinatario?: string | null;
  email_destinatario?: string | null;
  fecha_prestamo: string;
  fecha_prevista_devolucion?: string | null;
  fecha_devolucion?: string | null;
  estado: EstadoPrestamo;
}