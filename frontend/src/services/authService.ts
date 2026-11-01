import { api } from '../api/client';
import { TokenResponse, Usuario } from '../types';

export const authService = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>('/auth/login', {
      email,
      password,
    });
    return data;
  },

  obtenerPerfil: async (): Promise<Usuario> => {
    const { data } = await api.get<Usuario>('/auth/me');
    return data;
  },
};