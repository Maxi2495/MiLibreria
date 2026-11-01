import { api } from '../api/client';
import { Biblioteca, Estante } from '../types';

export const bibliotecaService = {
  listarBibliotecas: async (): Promise<Biblioteca[]> => {
    const { data } = await api.get<Biblioteca[]>('/api/v1/espacios/bibliotecas');
    return data;
  },

  crearBiblioteca: async (nombre: string): Promise<Biblioteca> => {
    const { data } = await api.post<Biblioteca>('/api/v1/espacios/bibliotecas', { nombre });
    return data;
  },

  agregarEstante: async (bibliotecaId: number, nombre: string, capacidad: number): Promise<Estante> => {
    const { data } = await api.post<Estante>(`/api/v1/espacios/bibliotecas/${bibliotecaId}/estantes`, {
      nombre,
      capacidad,
    });
    return data;
  },
};