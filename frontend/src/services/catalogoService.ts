import { api } from '../api/client';
import { Libro, LibroISBNResponse } from '../types';

export const catalogoService = {
  buscarPorISBN: async (isbn: string): Promise<LibroISBNResponse> => {
    const { data } = await api.get<LibroISBNResponse>(`/api/v1/catalogo/isbn/${isbn}`);
    return data;
  },

  listarLibros: async (params?: { buscar?: string }): Promise<Libro[]> => {
    const { data } = await api.get<Libro[]>('/api/v1/catalogo/libros', { params });
    return data;
  },

  crearLibro: async (payload: {
    titulo: string;
    isbn?: string;
    autores_ids: number[];
    generos_ids?: number[];
    editorial_id?: number;
    sinopsis?: string;
    portada_url?: string;
  }): Promise<Libro> => {
    const { data } = await api.post<Libro>('/api/v1/catalogo/libros', payload);
    return data;
  },
};