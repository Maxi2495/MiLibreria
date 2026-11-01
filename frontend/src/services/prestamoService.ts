import { api } from '../api/client';
import { Prestamo } from '../types';

export const prestamoService = {
  listarPrestamos: async (usuarioId: number, estado?: string): Promise<Prestamo[]> => {
    const { data } = await api.get<Prestamo[]>('/api/v1/prestamos/', {
      params: { usuario_id: usuarioId, estado },
    });
    return data;
  },

  registrarPrestamo: async (
    usuarioId: number,
    payload: {
      ejemplar_id: number;
      nombre_destinatario: string;
      apellido_destinatario: string;
      telefono_destinatario?: string;
      email_destinatario?: string;
      fecha_prevista_devolucion?: string;
    }
  ): Promise<Prestamo> => {
    const { data } = await api.post<Prestamo>('/api/v1/prestamos/', payload, {
      params: { usuario_id: usuarioId },
    });
    return data;
  },

  registrarDevolucion: async (
    prestamoId: number,
    usuarioId: number,
    estanteId?: number | null
  ): Promise<Prestamo> => {
    const { data } = await api.post<Prestamo>(
      `/api/v1/prestamos/${prestamoId}/devolucion`,
      { estante_id: estanteId ?? null },
      { params: { usuario_id: usuarioId } }
    );
    return data;
  },
};