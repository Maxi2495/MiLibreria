import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/authService';
import { LogIn, Loader2, AlertCircle } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const tokenData = await authService.login(email, password);
      localStorage.setItem('booknest_token', tokenData.access_token);
      
      const userData = await authService.obtenerPerfil();
      login(tokenData.access_token, userData);
      navigate('/catalogo', { replace: true });
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Credenciales inválidas o servidor no disponible.'
      );
      localStorage.removeItem('booknest_token');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-stone-900/90 rounded-2xl shadow-2xl border border-amber-900/40 backdrop-blur-md overflow-hidden">
        <div className="bg-stone-950/80 p-8 text-center text-white border-b border-amber-950/40">
          <div className="w-12 h-12 bg-amber-600 rounded-xl mx-auto flex items-center justify-center font-bold text-2xl mb-3 shadow-lg text-stone-950">
            B
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-amber-50">BookNest</h1>
          <p className="text-amber-200/70 text-sm mt-1">Gestión de Bibliotecas Personales Físicas</p>
        </div>

        <form onSubmit={handleSubmit} className="p-8 space-y-5">
          {error && (
            <div className="p-3 bg-red-950/80 border border-red-500/50 rounded-lg flex items-center gap-2 text-sm text-red-200">
              <AlertCircle size={18} className="shrink-0 text-red-400" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-amber-100 uppercase tracking-wider mb-1.5">
              Correo Electrónico
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu_email@ejemplo.com"
              required
              className="w-full px-3.5 py-2.5 border border-amber-950/50 rounded-lg text-sm bg-stone-100 text-slate-900 placeholder-slate-500 outline-none focus:ring-2 focus:ring-amber-500 font-medium"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-amber-100 uppercase tracking-wider mb-1.5">
              Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full px-3.5 py-2.5 border border-amber-950/50 rounded-lg text-sm bg-stone-100 text-slate-900 placeholder-slate-500 outline-none focus:ring-2 focus:ring-amber-500 font-medium"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-amber-600 text-stone-950 font-bold py-2.5 rounded-lg text-sm hover:bg-amber-500 transition flex items-center justify-center gap-2 disabled:opacity-50 shadow-md mt-2"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : <LogIn size={18} />}
            Ingresar al Sistema
          </button>
        </form>
      </div>
    </div>
  );
};