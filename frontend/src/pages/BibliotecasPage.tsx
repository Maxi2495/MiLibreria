import React, { useEffect, useState } from 'react';
import { bibliotecaService } from '../services/bibliotecaService';
import { Biblioteca } from '../types';
import { ProgressBar } from '../components/common/ProgressBar';
import { Layers } from 'lucide-react';

export const BibliotecasPage: React.FC = () => {
  const [bibliotecas, setBibliotecas] = useState<Biblioteca[]>([]);
  const [loading, setLoading] = useState(true);

  const cargar = async () => {
    try {
      const data = await bibliotecaService.listarBibliotecas();
      setBibliotecas(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-amber-50 drop-shadow-sm tracking-tight">
          Ubicación Física de Colecciones
        </h1>
        <p className="text-sm text-amber-200/80 mt-1 font-medium">
          Gestión de muebles, estanterías y control de aforo por sección.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-16 text-amber-200/70 font-medium">Cargando ubicaciones...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {bibliotecas.map((biblio) => (
            <div key={biblio.id} className="bg-stone-100 rounded-2xl shadow-xl border border-amber-950/20 p-6 space-y-4">
              <div className="flex items-center gap-2.5 border-b border-stone-200 pb-3">
                <Layers className="text-amber-800" size={22} />
                <h2 className="font-bold text-lg text-slate-900">{biblio.nombre}</h2>
              </div>

              <div className="space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Estantes asignados
                </h3>
                {biblio.estantes.length === 0 ? (
                  <p className="text-xs text-slate-500 italic py-2">
                    No hay estantes dados de alta en este mueble.
                  </p>
                ) : (
                  biblio.estantes.map((estante) => (
                    <div key={estante.id} className="p-3.5 bg-white rounded-xl border border-slate-200 shadow-sm">
                      <span className="font-semibold text-sm text-slate-900 block mb-2">{estante.nombre}</span>
                      <ProgressBar
                        actual={0}
                        max={estante.capacidad}
                      />
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};