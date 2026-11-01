import React, { useEffect, useState } from 'react';
import { prestamoService } from '../services/prestamoService';
import { useAuth } from '../context/AuthContext';
import { Prestamo } from '../types';
import { CheckCircle2, Clock, AlertTriangle } from 'lucide-react';

export const PrestamosPage: React.FC = () => {
  const { user } = useAuth();
  const [prestamos, setPrestamos] = useState<Prestamo[]>([]);
  const [loading, setLoading] = useState(true);

  const cargar = async () => {
    if (!user) return;
    try {
      const data = await prestamoService.listarPrestamos(user.id);
      setPrestamos(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargar();
  }, [user]);

  const devolver = async (id: number) => {
    if (!user) return;
    if (confirm('¿Confirmar recepción y reincorporación del ejemplar?')) {
      await prestamoService.registrarDevolucion(id, user.id);
      cargar();
    }
  };

  const getBadgeEstado = (estado: Prestamo['estado']) => {
    switch (estado) {
      case 'ACTIVO':
        return <span className="px-2.5 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded-full flex items-center gap-1 w-fit"><Clock size={12} /> Activo</span>;
      case 'DEVUELTO':
        return <span className="px-2.5 py-1 text-xs font-semibold bg-emerald-100 text-emerald-800 rounded-full flex items-center gap-1 w-fit"><CheckCircle2 size={12} /> Devuelto</span>;
      case 'VENCIDO':
        return <span className="px-2.5 py-1 text-xs font-semibold bg-red-100 text-red-800 rounded-full flex items-center gap-1 w-fit"><AlertTriangle size={12} /> Vencido</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-semibold bg-slate-100 text-slate-800 rounded-full">{estado}</span>;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-amber-50 drop-shadow-sm tracking-tight">
          Trazabilidad de Préstamos
        </h1>
        <p className="text-sm text-amber-200/80 mt-1 font-medium">
          Historial y control de ejemplares prestados a terceros.
        </p>
      </div>

      <div className="bg-stone-100 rounded-2xl shadow-xl border border-amber-950/20 overflow-hidden">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="bg-stone-200/80 border-b border-stone-300 text-xs text-slate-700 font-bold uppercase tracking-wider">
              <th className="p-4">Ejemplar</th>
              <th className="p-4">Prestatario</th>
              <th className="p-4">Fecha Préstamo</th>
              <th className="p-4">Devolución Pactada</th>
              <th className="p-4">Estado</th>
              <th className="p-4 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-200">
            {loading ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-slate-500">
                  Cargando préstamos...
                </td>
              </tr>
            ) : prestamos.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-slate-500">
                  No se registran préstamos en el historial.
                </td>
              </tr>
            ) : (
              prestamos.map((p) => (
                <tr key={p.id} className="hover:bg-white/60 transition">
                  <td className="p-4 font-semibold text-slate-900">
                    Ejemplar #{p.ejemplar_id}
                  </td>
                  <td className="p-4">
                    <span className="block font-medium text-slate-800">
                      {p.nombre_destinatario} {p.apellido_destinatario}
                    </span>
                    <span className="text-xs text-slate-500">
                      {p.email_destinatario || p.telefono_destinatario || 'Sin contacto'}
                    </span>
                  </td>
                  <td className="p-4 text-slate-700">{p.fecha_prestamo}</td>
                  <td className="p-4 text-slate-700">{p.fecha_prevista_devolucion || 'Sin fecha'}</td>
                  <td className="p-4">{getBadgeEstado(p.estado)}</td>
                  <td className="p-4 text-right">
                    {p.estado === 'ACTIVO' && (
                      <button
                        onClick={() => devolver(p.id)}
                        className="text-xs bg-slate-900 text-amber-50 font-semibold px-3 py-1.5 rounded-lg hover:bg-slate-800 transition shadow"
                      >
                        Registrar Devolución
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};